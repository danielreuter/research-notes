// The int8-Strassen replay's device measurements: the pieces that pin F2's c_L (and F1'/F2's margin over the flat-scale
// route) on the card, against the NVFP4 dense divisor.
//   leaf   the int8 GEMM (s8 x s8 -> s32, cuBLASLt IMMA) wall time at m=n=k; the ratio to the NVFP4 dense GEMM of the same
//          shape is the leaf cost in FP4 slots per MAC (NVFP4 dense = 1). c_L's leaf term is that ratio x (7/8)^L.
//   preadd the Strassen pre-add: an s8 elementwise add C = sat(A + B) over an m x k operand, timed as slots/MAC = its
//          bytes' share of a k-GEMM's MACs. Packed 4 int8 per 32-bit lane is the model's 4.25-slot assumption.
//   postadd the merge: an s32 accumulate D += S over m x n, the explicit-post-add price if C-operand seeding is unavailable.
// Prints one JSON line per (op, shape). The caller reuses the CUTLASS NVFP4 dense times (basesplit_e2e_sm120 dense128) for
// the divisor, and computes c_L(m,k,n) = min over 1<=L<=log2(k/16) of leaf*(7/8)^L + preadd_slots*(1/m+1/n)*((7/4)^L-1)/0.75.
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <utility>
#include <cuda_runtime.h>
#include <cublasLt.h>

#define CK(x) do { cudaError_t e=(x); if(e!=cudaSuccess){fprintf(stderr,"cuda %s:%d %s\n",__FILE__,__LINE__,cudaGetErrorString(e));exit(2);} } while(0)
#define LK(x) do { cublasStatus_t s=(x); if(s!=CUBLAS_STATUS_SUCCESS){fprintf(stderr,"cublasLt %s:%d %d\n",__FILE__,__LINE__,(int)s);exit(2);} } while(0)

static float time_ms(int iters, cudaStream_t s, void(*run)(void*), void* ctx){
  for(int i=0;i<5;i++) run(ctx);
  CK(cudaStreamSynchronize(s));
  cudaEvent_t a,b; cudaEventCreate(&a); cudaEventCreate(&b);
  cudaEventRecord(a,s);
  for(int i=0;i<iters;i++) run(ctx);
  cudaEventRecord(b,s); cudaEventSynchronize(b);
  float ms; cudaEventElapsedTime(&ms,a,b); return ms/iters;
}

struct LtGemm {
  cublasLtHandle_t lt; cublasLtMatmulDesc_t op; cublasLtMatrixLayout_t la,lb,lc;
  void *A,*B,*C,*ws; size_t wsz; cublasLtMatmulAlgo_t algo; bool have_algo=false; cudaStream_t s;
};
static void run_gemm(void* p){
  LtGemm* g=(LtGemm*)p; int32_t alpha=1,beta=0;
  LK(cublasLtMatmul(g->lt,g->op,&alpha,g->A,g->la,g->B,g->lb,&beta,g->C,g->lc,g->C,g->lc,
     g->have_algo?&g->algo:nullptr,g->ws,g->wsz,g->s));
}

static float int8_gemm(int m,int n,int k,int iters,cudaStream_t s,int batch=1){
  LtGemm g; g.s=s; LK(cublasLtCreate(&g.lt));
  size_t sa=(size_t)m*k, sb=(size_t)k*n, sc=(size_t)m*n;
  CK(cudaMalloc(&g.A,sa*batch)); CK(cudaMalloc(&g.B,sb*batch)); CK(cudaMalloc(&g.C,sc*batch*4));
  CK(cudaMemset(g.A,1,sa*batch)); CK(cudaMemset(g.B,1,sb*batch));
  g.wsz=(size_t)1<<30; CK(cudaMalloc(&g.ws,g.wsz));
  LK(cublasLtMatmulDescCreate(&g.op,CUBLAS_COMPUTE_32I,CUDA_R_32I));
  cublasOperation_t tn=CUBLAS_OP_T,nn=CUBLAS_OP_N;
  LK(cublasLtMatmulDescSetAttribute(g.op,CUBLASLT_MATMUL_DESC_TRANSA,&tn,sizeof(tn)));   // A^T: k x m col-major = m x k row-major
  LK(cublasLtMatmulDescSetAttribute(g.op,CUBLASLT_MATMUL_DESC_TRANSB,&nn,sizeof(nn)));
  LK(cublasLtMatrixLayoutCreate(&g.la,CUDA_R_8I,k,m,k));
  LK(cublasLtMatrixLayoutCreate(&g.lb,CUDA_R_8I,k,n,k));
  LK(cublasLtMatrixLayoutCreate(&g.lc,CUDA_R_32I,m,n,m));
  if(batch>1){
    int64_t oa=sa,ob=sb,oc=sc;
    for(auto pr: {std::make_pair(g.la,oa),std::make_pair(g.lb,ob),std::make_pair(g.lc,oc)}){
      LK(cublasLtMatrixLayoutSetAttribute(pr.first,CUBLASLT_MATRIX_LAYOUT_BATCH_COUNT,&batch,sizeof(batch)));
      LK(cublasLtMatrixLayoutSetAttribute(pr.first,CUBLASLT_MATRIX_LAYOUT_STRIDED_BATCH_OFFSET,&pr.second,sizeof(pr.second)));
    }
  }
  cublasLtMatmulPreference_t pref; LK(cublasLtMatmulPreferenceCreate(&pref));
  LK(cublasLtMatmulPreferenceSetAttribute(pref,CUBLASLT_MATMUL_PREF_MAX_WORKSPACE_BYTES,&g.wsz,sizeof(g.wsz)));
  cublasLtMatmulHeuristicResult_t h[1]; int got=0;
  LK(cublasLtMatmulAlgoGetHeuristic(g.lt,g.op,g.la,g.lb,g.lc,g.lc,pref,1,h,&got));
  if(got>0){ g.algo=h[0].algo; g.have_algo=true; }
  float ms=time_ms(iters,s,run_gemm,&g);
  cudaFree(g.A);cudaFree(g.B);cudaFree(g.C);cudaFree(g.ws);
  return ms;
}

// s8 saturating add over n bytes, 4 per 32-bit lane (the packed pre-add)
__global__ void s8add(const char4* a,const char4* b,char4* c,size_t n4){
  size_t i=blockIdx.x*(size_t)blockDim.x+threadIdx.x;
  if(i>=n4) return;
  char4 x=a[i],y=b[i],z;
  z.x=(char)max(-127,min(127,x.x+y.x)); z.y=(char)max(-127,min(127,x.y+y.y));
  z.z=(char)max(-127,min(127,x.z+y.z)); z.w=(char)max(-127,min(127,x.w+y.w));
  c[i]=z;
}
__global__ void s32add(const int* a,int* c,size_t n){
  size_t i=blockIdx.x*(size_t)blockDim.x+threadIdx.x; if(i<n) c[i]+=a[i];
}
struct AddCtx{ void*a;void*b;void*c;size_t n;int kind;cudaStream_t s; };
static void run_add(void* p){
  AddCtx* q=(AddCtx*)p;
  if(q->kind==8){ size_t n4=q->n/4; s8add<<<(n4+255)/256,256,0,q->s>>>((char4*)q->a,(char4*)q->b,(char4*)q->c,n4); }
  else { s32add<<<(q->n+255)/256,256,0,q->s>>>((int*)q->a,(int*)q->c,q->n); }
}
static float add_ms(size_t n,int kind,int iters,cudaStream_t s){
  AddCtx q; q.n=n; q.kind=kind; q.s=s; size_t es=(kind==8)?1:4;
  CK(cudaMalloc(&q.a,n*es)); CK(cudaMalloc(&q.b,n*es)); CK(cudaMalloc(&q.c,n*es));
  CK(cudaMemset(q.a,1,n*es)); CK(cudaMemset(q.b,1,n*es)); CK(cudaMemset(q.c,0,n*es));
  float ms=time_ms(iters,s,run_add,&q);
  cudaFree(q.a);cudaFree(q.b);cudaFree(q.c); return ms;
}

int main(int argc,char**argv){
  cudaStream_t s; CK(cudaStreamCreate(&s));
  std::vector<int> shapes; for(int i=1;i<argc;i++) shapes.push_back(atoi(argv[i]));
  if(shapes.empty()) shapes={8192,16384};
  for(int S:shapes){
    int it = S<=8192?50: S<=16384?20:8;
    float g=int8_gemm(S,S,S,it,s);
    double tops = 2.0*(double)S*S*S/(g*1e-3)/1e12;
    printf("{\"op\":\"int8_gemm\",\"m\":%d,\"n\":%d,\"k\":%d,\"ms\":%.5f,\"tops\":%.1f}\n",S,S,S,g,tops); fflush(stdout);
    float p8=add_ms((size_t)S*S,8,it,s);      // one m x k operand's s8 pre-add
    float p32=add_ms((size_t)S*S,32,it,s);    // one m x n s32 merge
    printf("{\"op\":\"s8_preadd\",\"elems\":%lld,\"ms\":%.5f}\n",(long long)S*S,p8);
    printf("{\"op\":\"s32_merge\",\"elems\":%lld,\"ms\":%.5f}\n",(long long)S*S,p32); fflush(stdout);
  }
  // batched leaves: the same MAC count as one 8192^3 GEMM, cut into 7^L-style small GEMMs
  for(int leaf: {1024,512,256,128,64}){
    long long total=(long long)8192*8192*8192; int batch=(int)(total/((long long)leaf*leaf*leaf));
    if(batch>32768) batch=32768;
    float g=int8_gemm(leaf,leaf,leaf,10,s,batch);
    double tops=2.0*(double)leaf*leaf*leaf*batch/(g*1e-3)/1e12;
    printf("{\"op\":\"int8_batched_leaf\",\"leaf\":%d,\"batch\":%d,\"ms\":%.5f,\"tops\":%.1f}\n",leaf,batch,g,tops); fflush(stdout);
  }
  return 0;
}
