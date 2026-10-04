// Issue rates of the CUDA-core instructions that can write a Strassen pre-add on sm_120: packed half add (HADD2, f16x2 and
// bf16x2), packed half FMA (HFMA2), FP32 add (FADD) and FMA (FFMA). Thread-instructions per SM per clock, with 16 warps
// per SM on every SM, 8 independent chains per thread so latency is hidden. The price per written element in W1 (E4M3
// MAC units) is 1,016 / rate / values-per-instruction: HADD2 writes 2 values, FADD 1. bc-3006c44a's pre-add floor is 4 W1
// per element if a packed half add issues at 128; it is 8 at 64.
#include <cstdio>
#include <cuda_fp16.h>
#include <cuda_bf16.h>
#define CK(x) do{cudaError_t e=(x); if(e!=cudaSuccess){printf("cuda %s\n",cudaGetErrorString(e)); return 1;}}while(0)
constexpr int ITERS = 4096, CH = 8;

__global__ void k_hadd2(__half2* out, __half2 d){
  __half2 a[CH]; for(int c=0;c<CH;c++) a[c]=__halves2half2(__float2half(threadIdx.x*1e-3f+c),__float2half(1.0f));
  for(int i=0;i<ITERS;i++){
    #pragma unroll
    for(int c=0;c<CH;c++) a[c]=__hadd2(a[c],d);
  }
  __half2 s=a[0]; for(int c=1;c<CH;c++) s=__hadd2(s,a[c]); out[blockIdx.x*blockDim.x+threadIdx.x]=s;
}
__global__ void k_badd2(__nv_bfloat162* out, __nv_bfloat162 d){
  __nv_bfloat162 a[CH]; for(int c=0;c<CH;c++) a[c]=__floats2bfloat162_rn(threadIdx.x*1e-3f+c,1.0f);
  for(int i=0;i<ITERS;i++){
    #pragma unroll
    for(int c=0;c<CH;c++) a[c]=__hadd2(a[c],d);
  }
  __nv_bfloat162 s=a[0]; for(int c=1;c<CH;c++) s=__hadd2(s,a[c]); out[blockIdx.x*blockDim.x+threadIdx.x]=s;
}
__global__ void k_hfma2(__half2* out, __half2 m, __half2 d){
  __half2 a[CH]; for(int c=0;c<CH;c++) a[c]=__halves2half2(__float2half(threadIdx.x*1e-3f+c),__float2half(1.0f));
  for(int i=0;i<ITERS;i++){
    #pragma unroll
    for(int c=0;c<CH;c++) a[c]=__hfma2(a[c],m,d);
  }
  __half2 s=a[0]; for(int c=1;c<CH;c++) s=__hadd2(s,a[c]); out[blockIdx.x*blockDim.x+threadIdx.x]=s;
}
__global__ void k_fadd(float* out, float d){
  float a[CH]; for(int c=0;c<CH;c++) a[c]=threadIdx.x*1e-3f+c;
  for(int i=0;i<ITERS;i++){
    #pragma unroll
    for(int c=0;c<CH;c++) a[c]=__fadd_rn(a[c],d);
  }
  float s=0; for(int c=0;c<CH;c++) s+=a[c]; out[blockIdx.x*blockDim.x+threadIdx.x]=s;
}
__global__ void k_ffma(float* out, float m, float d){
  float a[CH]; for(int c=0;c<CH;c++) a[c]=threadIdx.x*1e-3f+c;
  for(int i=0;i<ITERS;i++){
    #pragma unroll
    for(int c=0;c<CH;c++) a[c]=__fmaf_rn(a[c],m,d);
  }
  float s=0; for(int c=0;c<CH;c++) s+=a[c]; out[blockIdx.x*blockDim.x+threadIdx.x]=s;
}

int main(){
  cudaDeviceProp p; CK(cudaGetDeviceProperties(&p,0));
  int sms=p.multiProcessorCount, threads=512, blocks=sms;       // 16 warps per SM
  int clk_khz=0; cudaDeviceGetAttribute(&clk_khz,cudaDevAttrClockRate,0);
  void* buf; CK(cudaMalloc(&buf,(size_t)blocks*threads*8));
  cudaEvent_t a,b; cudaEventCreate(&a); cudaEventCreate(&b);
  const char* names[]={"HADD2.f16x2","HADD2.bf16x2","HFMA2.f16x2","FADD","FFMA"};
  int vals[]={2,2,2,1,1};
  for(int kk=0;kk<5;kk++){
    float best=1e30f;
    for(int rep=0;rep<5;rep++){
      cudaEventRecord(a);
      if(kk==0) k_hadd2<<<blocks,threads>>>((__half2*)buf,__halves2half2(__float2half(1e-4f),__float2half(1e-4f)));
      if(kk==1) k_badd2<<<blocks,threads>>>((__nv_bfloat162*)buf,__floats2bfloat162_rn(1e-4f,1e-4f));
      if(kk==2) k_hfma2<<<blocks,threads>>>((__half2*)buf,__halves2half2(__float2half(1.0f),__float2half(1.0f)),__halves2half2(__float2half(1e-4f),__float2half(1e-4f)));
      if(kk==3) k_fadd<<<blocks,threads>>>((float*)buf,1e-4f);
      if(kk==4) k_ffma<<<blocks,threads>>>((float*)buf,1.0f,1e-4f);
      cudaEventRecord(b); cudaEventSynchronize(b);
      float ms; cudaEventElapsedTime(&ms,a,b); if(rep>0 && ms<best) best=ms;
    }
    double instr=(double)blocks*threads*ITERS*CH;
    // SM clock from the measured nvidia-smi sampler is the reference; the attribute is the max boost clock
    double per_sm_per_clk = instr/(best*1e-3)/sms/(clk_khz*1e3);
    printf("{\"op\":\"%s\",\"ms\":%.4f,\"thread_instr_per_sm_per_clk_at_attr_clock\":%.2f,\"attr_clock_mhz\":%.0f,\"values_per_instr\":%d,"
           "\"W1_per_element_at_1016\":%.2f}\n",names[kk],best,per_sm_per_clk,clk_khz/1e3,vals[kk],1016.0/per_sm_per_clk/vals[kk]);
  }
  return 0;
}
