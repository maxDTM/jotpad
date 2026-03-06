Name:           jotpad
Version:        1.0.0
Release:        1%{?dist}
Summary:        Minimal single-note editor with live markdown formatting
License:        GPL-3.0-or-later
URL:            https://github.com/maxDTM/jotpad
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-pip
Requires:       python3 >= 3.9
Requires:       python3-pyside6

%description
Jotpad is a minimal desktop note editor that manages a single persistent
note file. It auto-saves when typing stops and provides live inline
markdown formatting with clickable hyperlinks.

%prep
%autosetup -n %{name}-%{version}

%build
%py3_build_wheel

%install
%py3_install_wheel %{name}-%{version}-*.whl

install -Dm644 data/com.jotpad.Jotpad.desktop \
    %{buildroot}%{_datadir}/applications/com.jotpad.Jotpad.desktop

install -Dm644 data/icons/jotpad.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/jotpad.svg

install -Dm644 man/jotpad.1 \
    %{buildroot}%{_mandir}/man1/jotpad.1

%files
%license LICENSE
%doc README.md
%{_bindir}/jotpad
%{python3_sitelib}/jotpad/
%{python3_sitelib}/jotpad-*.dist-info/
%{_datadir}/applications/com.jotpad.Jotpad.desktop
%{_datadir}/icons/hicolor/scalable/apps/jotpad.svg
%{_mandir}/man1/jotpad.1*

%changelog
* Thu Jan 01 2025 Max Altshuler - 1.0.0-1
- Initial release
