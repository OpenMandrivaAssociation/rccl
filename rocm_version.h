/* Minimal FHS stand-in for rocm-core/rocm_version.h (OM has no rocm-core package). */
#ifndef ROCM_CORE_ROCM_VERSION_H
#define ROCM_CORE_ROCM_VERSION_H
#define ROCM_VERSION_MAJOR 10
#define ROCM_VERSION_MINOR 0
#define ROCM_VERSION_PATCH 0
#ifndef ROCM_BUILD_INFO
#define ROCM_BUILD_INFO "10.0.0-openmandriva"
#endif
/* librocm-core API used by src/init.cc when ROCM_VERSION >= 60000. */
#ifndef VerSuccess
#define VerSuccess 0
#endif
#ifdef __cplusplus
static inline int getROCmVersion(unsigned int* major, unsigned int* minor, unsigned int* patch)
{
	if (major)
		*major = ROCM_VERSION_MAJOR;
	if (minor)
		*minor = ROCM_VERSION_MINOR;
	if (patch)
		*patch = ROCM_VERSION_PATCH;
	return VerSuccess;
}
#endif
#endif
