/* mnestra.h — C ABI for the Mnestra memory interface.
 *
 * The C ABI is the lingua franca that lets every other language (Rust, Go, Python/cffi,
 * Java/JNI, Node N-API, Swift, ...) bind the same substrate-agnostic memory. A substrate
 * driver (classical / photonic / quantum) provides one implementation of these symbols.
 */
#ifndef MNESTRA_H
#define MNESTRA_H
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum { MNESTRA_CLASSICAL = 0, MNESTRA_PHOTONIC = 1, MNESTRA_QUANTUM_AFC = 2 } mnestra_substrate;
typedef struct mnestra mnestra; /* opaque handle */

typedef struct { char address[33]; float score; } mnestra_recall;

mnestra *mnestra_open(mnestra_substrate s);
void          mnestra_close(mnestra *m);

/* write a pattern; writes the 33-byte (incl NUL) content address into out_addr */
int  mnestra_write(mnestra *m, const char *text, const char *summary, char out_addr[33]);
/* read by exact address; returns malloc'd ACF-JSON or NULL (caller frees) */
char *mnestra_read(mnestra *m, const char *address);
/* associative recall; fills up to k results, returns count */
int  mnestra_query(mnestra *m, const char *cue, int k, mnestra_recall *out, int out_cap);
/* structure-complete global view as ACF-JSON (caller frees) */
char *mnestra_reconstruct(mnestra *m);

#ifdef __cplusplus
}
#endif
#endif /* MNESTRA_H */
