# RCCL — ROCm Communication Collectives (NCCL for HIP)
# Upstream has no therock-7.14 tarball; use rocm-7.2.4 (NCCL 2.27.7), which
# matches the 7.x HIP/runtime APIs used by TheRock 7.14.

# Multi-arch fat HIP + global -flto stalls for hours in ld.lld per gfx*
%define _disable_lto 1

Name:		rccl
Version:	7.14.0
Release:	1
%{!?rocm_llvm_maj_ver:%global rocm_llvm_maj_ver 23}
Summary:	ROCm Communication Collectives Library (NCCL for HIP)
License:	BSD-3-Clause AND MIT
Group:		System/Libraries
URL:		https://github.com/ROCm/rccl
# Closest released tag to TheRock 7.14 (no therock-7.14 asset on this repo)
Source0:	https://github.com/ROCm/rccl/archive/refs/tags/rocm-7.2.4.tar.gz#/rccl-%{version}.tar.gz
# Build-time hipify (not yet packaged separately on OM)
Source1:	hipify-perl
# Skip upstream toolchain-linux.cmake (/opt/rocm amdclang defaults)
Source2:	empty-toolchain.cmake
# FHS stub for <rocm-core/rocm_version.h> (no rocm-core package on OM)
Source3:	rocm_version.h

BuildRequires:	rocm-rpm-macros
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	git-core
BuildRequires:	rocm-cmake
BuildRequires:	hipcc
BuildRequires:	rocminfo
BuildRequires:	clang-tools
BuildRequires:	rocm-hip-devel
BuildRequires:	rocm-runtime-devel
BuildRequires:	rocm-smi-devel
BuildRequires:	clang >= %{rocm_llvm_maj_ver}
BuildRequires:	perl
BuildRequires:	python3

ExclusiveArch:	%{x86_64} %{aarch64}

%description
RCCL implements multi-GPU / multi-node collective operations (all-reduce,
broadcast, all-gather, …) for HIP, API-compatible with NCCL.
GPU targets: gfx803 (Polaris) + gfx1100/1101/1200/1201. Full matrix is in
%%rocm_gpu_targets_rccl for ABF multi-hour fat builds.

Built from upstream tag rocm-7.2.4 (lib version 2.27.7); packaged as
%{version} to track the OpenMandriva TheRock 7.14 stack.

%package devel
Summary:	Development files for RCCL
Group:		Development/C++
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	rocm-hip-devel
Provides:	rccl-devel = %{EVRD}

%description devel
Headers and CMake package for RCCL.

%prep
%autosetup -n rccl-rocm-7.2.4 -p1
# hipify-perl on PATH for the build
install -m 755 %{SOURCE1} %{_builddir}/hipify-perl
# Stub rocm-core version header used by hip_rocm_version_info.h
mkdir -p %{_builddir}/include-stub/rocm-core
cp -a %{SOURCE3} %{_builddir}/include-stub/rocm-core/rocm_version.h

%build
export PATH="%{_builddir}:$PATH"
export ROCM_PATH=%{_prefix}
export HIP_PATH=%{_prefix}
export HIP_DEVICE_LIB_PATH=%{_libdir}/amdgcn/bitcode
export CXX=hipcc
export CC=clang
export HIPCXX=clang
CXXFLAGS=$(printf '%s' "%{optflags}" | sed -E 's/-mfpmath=[^ ]+//g; s/ -m[a-z0-9+.=]+//g')
CXXFLAGS="$CXXFLAGS -I%{_builddir}/include-stub"
export CXXFLAGS
export CFLAGS="$CXXFLAGS"
export LDFLAGS=$(printf '%s' "%{?__global_ldflags}" | sed -E 's/-mfpmath=[^ ]+//g; s/ -m[a-z0-9+.=]+//g')

# Imperative cmake: OM %%cmake macro can drop trailing -D flags with ';' values
mkdir -p build
cd build
RCCL_GPU_TARGETS='gfx803;gfx1100;gfx1101;gfx1200;gfx1201'
/usr/bin/cmake .. \
	-DCMAKE_SKIP_RPATH=ON \
	-DCMAKE_INSTALL_PREFIX=%{_prefix} \
	-DCMAKE_INSTALL_LIBDIR=%{_lib} \
	-DFILE_REORG_BACKWARD_COMPATIBILITY=OFF \
	-DINCLUDE_PATH_COMPATIBILITY=OFF \
	-DROCM_SYMLINK_LIBS=OFF \
	-DCMAKE_TOOLCHAIN_FILE=%{SOURCE2} \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_CXX_COMPILER=/usr/bin/hipcc \
	-DCMAKE_C_COMPILER=/usr/bin/clang \
	-DCMAKE_CXX_FLAGS="$CXXFLAGS" \
	-DGPU_TARGETS="${RCCL_GPU_TARGETS}" \
	-DEXPLICIT_ROCM_VERSION=%{version} \
	-DBUILD_TESTS=OFF \
	-DBUILD_SHARED_LIBS=ON \
	-DENABLE_MSCCLPP=OFF \
	-DENABLE_MSCCL_KERNEL=ON \
	-DCOLLTRACE=ON \
	-DROCTX=OFF \
	-DROCM_PATH=%{_prefix} \
	-DCMAKE_PREFIX_PATH=%{_prefix} \
	-G Ninja
/usr/bin/ninja -j%{?_smp_build_ncpus}%{!?_smp_build_ncpus:16}
cd ..

%install
cd build
DESTDIR=%{buildroot} /usr/bin/ninja install -j%{?_smp_build_ncpus}%{!?_smp_build_ncpus:8}
cd ..
# Normalize cmake package path if upstream dropped under /usr/lib
if [ -d %{buildroot}/usr/lib/cmake/rccl ] && [ ! -d %{buildroot}%{_libdir}/cmake/rccl ]; then
	mkdir -p %{buildroot}%{_libdir}/cmake
	mv %{buildroot}/usr/lib/cmake/rccl %{buildroot}%{_libdir}/cmake/
	rmdir %{buildroot}/usr/lib/cmake 2>/dev/null || true
	rmdir %{buildroot}/usr/lib 2>/dev/null || true
fi

%files
%license LICENSE.txt
%doc README.md CHANGELOG.md
%{_libdir}/librccl.so.*
# MSCCL algorithm data
%{_datadir}/rccl/

%files devel
%{_includedir}/rccl/
%{_libdir}/librccl.so
%{_libdir}/cmake/rccl/
