/* n2h_loopback.so (proofs-n2-hill): LD_PRELOAD shim that moves a job's IPv4 loopback traffic to its slot's own address.
 *
 * Node 1 runs each prover job in a pod network namespace of its own, so 74-gemm-hill.sh's fixed ports (7720, 7721) on
 * 127.0.0.1 never meet. Node 2 has one shared host network and no unprivileged network namespaces (AppArmor restricts
 * unprivileged user namespaces), so bind() and connect() to 127.0.0.1:<port> become N2H_LOOPBACK:<port>
 * (127.77.<slot+1>.1, which nothing else on node 2 uses); ports and every other address are unchanged.
 *
 *   gcc -O2 -shared -fPIC -o n2h_loopback.so n2h_loopback.c -ldl
 */
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <dlfcn.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>

static in_addr_t slot_addr(void) {
    static in_addr_t a;
    static int done;
    if (!done) {
        struct in_addr x;
        const char *s = getenv("N2H_LOOPBACK");
        a = (s && inet_aton(s, &x)) ? x.s_addr : 0;
        done = 1;
    }
    return a;
}

static const struct sockaddr *fix(const struct sockaddr *sa, socklen_t len, struct sockaddr_in *buf) {
    in_addr_t a = slot_addr();
    if (!a || !sa || len < (socklen_t)sizeof(struct sockaddr_in) || sa->sa_family != AF_INET)
        return sa;
    if (((const struct sockaddr_in *)sa)->sin_addr.s_addr != htonl(INADDR_LOOPBACK))
        return sa;
    memcpy(buf, sa, sizeof *buf);
    buf->sin_addr.s_addr = a;
    return (const struct sockaddr *)buf;
}

int bind(int fd, const struct sockaddr *sa, socklen_t len) {
    static int (*real)(int, const struct sockaddr *, socklen_t);
    struct sockaddr_in b;
    if (!real)
        real = (int (*)(int, const struct sockaddr *, socklen_t))dlsym(RTLD_NEXT, "bind");
    return real(fd, fix(sa, len, &b), len);
}

int connect(int fd, const struct sockaddr *sa, socklen_t len) {
    static int (*real)(int, const struct sockaddr *, socklen_t);
    struct sockaddr_in b;
    if (!real)
        real = (int (*)(int, const struct sockaddr *, socklen_t))dlsym(RTLD_NEXT, "connect");
    return real(fd, fix(sa, len, &b), len);
}
