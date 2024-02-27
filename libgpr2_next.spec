# Upstream source information.
%global upstream_owner        AdaCore
%global upstream_name         gpr
%global upstream_commit_date  20240104
%global upstream_commit       5979451d7f3e27095f8eb48ab508f7c3e6266f83
%global upstream_shortcommit  %(c=%{upstream_commit}; echo ${c:0:7})

Name:           libgpr2_next
Version:        0^%{upstream_commit_date}git%{upstream_shortcommit}
Release:        1%{?dist}
Summary:        The GNAT project manager library

License:        Apache-2.0 WITH LLVM-Exception

URL:            https://github.com/%{upstream_owner}/%{upstream_name}
Source:         %{url}/archive/%{upstream_commit}.tar.gz#/%{name}-%{upstream_shortcommit}.tar.gz

# [Fedora-specific] Set the library so version.
Patch:          %{name}-set-library-so-version.patch

BuildRequires:  gcc-gnat gprbuild make sed
# A fedora-gnat-project-common that contains GPRbuild_flags is needed.
BuildRequires:  fedora-gnat-project-common >= 3.17
BuildRequires:  gprconfig-kb
BuildRequires:  gnatcoll-core-devel
BuildRequires:  gnatcoll-gmp-devel
BuildRequires:  gnatcoll-iconv-devel

# Build only on architectures where GPRbuild is available.
ExclusiveArch:  %{GPRbuild_arches}

# Cannot be installed with the "current" version of libgpr2.
Conflicts:      libgpr2

%global common_description_en \
An Ada library for handling GNAT project files.

%description %{common_description_en}


#################
## Subpackages ##
#################

%package devel
Summary:        Development files for the GNAT project manager library
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       fedora-gnat-project-common
Requires:       libgpr-devel
Requires:       gnatcoll-core-devel
Requires:       gnatcoll-gmp-devel
Requires:       gnatcoll-iconv-devel
Requires:       xmlada-devel

%description devel %{common_description_en}

This package contains source code and linking information for developing
applications that use the GNAT project manager library.


#############
## Prepare ##
#############

%prep
%autosetup -n %{upstream_name}-%{upstream_commit} p1

# Update some release specific information in the source code. The substitutions
# are scoped to specific lines to increase the chance of detecting code changes
# at this point. Sed should exit with exit code 0 if the substitution succeeded
# (using `t`, jump to end of script) or exit with a non-zero exit code if the
# substitution failed (using `q1`, quit with exit code 1).
sed --in-place \
    --expression='11 { s,18.0w,%{upstream_commit_date} (next), ; t; q1 }' \
    --expression='14 { s,19940713,%{upstream_release_date},    ; t; q1 }' \
    --expression='16 { s,"2016",Date (1 .. 4),                 ; t; q1 }' \
    --expression='21 { s,Gnatpro,GPL,                          ; t; q1 }' \
    src/lib/gpr2-version.ads

# Initialize some variables.
make LIBGPR2_TYPES='relocatable' PYTHON='%{python3}' \
     GPR2KBDIR='%{_datadir}/gprconfig' FORCE_PARSER_GEN=force \
     setup


###########
## Build ##
###########

%build

export VERSION=%{upstream_commit_date}

# Build the library.
%{make_build} GPRBUILD_OPTIONS='%{GPRbuild_flags}' build-lib-relocatable


#############
## Install ##
#############

%install

# Install the library.
gprinstall %{GPRinstall_flags} --no-build-var \
           -XVERSION=%{upstream_commit_date} -XGPR2_BUILD=release_checks \
           -XLIBRARY_TYPE=relocatable -XXMLADA_BUILD=relocatable \
           -P gpr2.gpr

# Fix up some things that GPRinstall does wrong.
ln --symbolic --force %{name}.so.%{upstream_commit_date} %{buildroot}%{_libdir}/%{name}.so

# Make the generated usage project file architecture-independent.
sed --regexp-extended --in-place \
    '--expression=1i with "directories";' \
    '--expression=/^--  This project has been generated/d' \
    '--expression=s|^( *for +Source_Dirs +use +).*;$|\1(Directories.Includedir \& "/%{name}");|i' \
    '--expression=s|^( *for +Library_Dir +use +).*;$|\1Directories.Libdir;|i' \
    '--expression=s|^( *for +Library_ALI_Dir +use +).*;$|\1Directories.Libdir \& "/%{name}";|i' \
    %{buildroot}%{_GNAT_project_dir}/gpr2.gpr
# The Sed commands are:
# 1: Insert a with clause before the first line to import the directories
#    project.
# 2: Delete a comment that mentions the architecture.
# 3: Replace the value of Source_Dirs with a pathname based on
#    Directories.Includedir.
# 4: Replace the value of Library_Dir with Directories.Libdir.
# 5: Replace the value of Library_ALI_Dir with a pathname based on
#    Directories.Libdir.


###########
## Files ##
###########

%files
%license LICENSE-lib
%doc README*
%{_libdir}/%{name}.so.%{upstream_commit_date}


%files devel
%{_GNAT_project_dir}/gpr2.gpr
%{_includedir}/%{name}
%dir %{_libdir}/%{name}
%attr(444,-,-) %{_libdir}/%{name}/*.ali
%{_libdir}/%{name}.so


###############
## Changelog ##
###############

%changelog
* Tue Feb 27 2024 Dennis van Raaij <dvraaij@fedoraproject.org> - 0^20240104git5979451-1
- Updated to snapshot: Git commit 5979451 (24.2-next), 2024-01-04.

* Tue Feb 27 2024 Dennis van Raaij <dvraaij@fedoraproject.org> - 0^20230509git092edbe-1
- New package, snapshot: Git commit 092edbe (next), 2023-05-09.
