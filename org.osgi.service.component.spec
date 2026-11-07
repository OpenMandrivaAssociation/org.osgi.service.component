Name:		org.osgi.service.component
Version:	1.5.1
Release:	1
Summary:	OSGi Declarative Services API
Group:		Development/Java
License:	ASL 2.0
URL:		https://docs.osgi.org/
Source0:	https://repo1.maven.org/maven2/org/osgi/org.osgi.service.component/%{version}/org.osgi.service.component-%{version}-sources.jar
Source1:	https://repo1.maven.org/maven2/org/osgi/org.osgi.service.component.annotations/%{version}/org.osgi.service.component.annotations-%{version}-sources.jar
Source2:	https://raw.githubusercontent.com/osgi/osgi/8.1.0.cmpn/LICENSE#/org.osgi.service.component-%{version}-LICENSE

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.osgi:osgi.core)
BuildRequires:	mvn(org.osgi:org.osgi.dto)
BuildRequires:	mvn(org.osgi:org.osgi.service.condition)
BuildRequires:	mvn(org.osgi:org.osgi.namespace.extender)
BuildRequires:	mvn(org.osgi:org.osgi.util.promise)
BuildRequires:	mvn(org.osgi:osgi.annotation)
BuildSystem:	maven
BuildOption(install):	--file-name %{name} --alias org.osgi:org.osgi.service.component.annotations

%description
OSGi Declarative Services 1.5.1. The runtime API and the component
annotations reference each other, so this package builds both source
trees into one jar. The annotations coordinate is an alias of that jar.
Framework types come from OSGi Core 6. The versioning annotations are
not required at runtime. This build targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} %{SOURCE1} <<'PY'
import sys
import zipfile
for name in sys.argv[1:]:
    zipfile.ZipFile(name).extractall(".")
PY
rm -rf META-INF
cp -p %{SOURCE2} LICENSE
mkdir -p src/main/java
mv org src/main/java/
python - <<'PY'
from pathlib import Path

java_files = list(Path("src/main/java").rglob("*.java"))
if len(java_files) != 38:
    raise SystemExit("java files " + str(len(java_files)))
for rel in (
    "src/main/java/org/osgi/service/component/ComponentConstants.java",
    "src/main/java/org/osgi/service/component/annotations/Component.java",
):
    if not Path(rel).is_file():
        raise SystemExit("missing " + rel)
if list(Path(".").rglob("*.jar")) or list(Path(".").rglob("*.class")):
    raise SystemExit("prebuilt binary remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.osgi</groupId>
  <artifactId>org.osgi.service.component</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>org.osgi:org.osgi.service.component</name>
  <description>OSGi Declarative Services API and component annotations.</description>
  <url>https://docs.osgi.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.core</artifactId>
      <version>6.0.0</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.dto</artifactId>
      <version>1.1.0</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.util.promise</artifactId>
      <version>1.3.0</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.service.condition</artifactId>
      <version>1.0.0</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.namespace.extender</artifactId>
      <version>1.0.1</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.annotation</artifactId>
      <version>8.1.0</version>
      <scope>provided</scope>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
poms = sorted(str(path) for path in Path(".").rglob("pom.xml"))
if poms != ["pom.xml"]:
    raise SystemExit("poms " + str(poms))
for needle in (
    "<artifactId>org.osgi.service.component</artifactId>",
    "<artifactId>osgi.core</artifactId>",
    "<version>6.0.0</version>",
    "<artifactId>org.osgi.dto</artifactId>",
    "<version>1.1.0</version>",
    "<artifactId>org.osgi.util.promise</artifactId>",
    "<version>1.3.0</version>",
    "<artifactId>org.osgi.service.condition</artifactId>",
    "<version>1.0.0</version>",
    "<artifactId>org.osgi.namespace.extender</artifactId>",
    "<version>1.0.1</version>",
    "<artifactId>osgi.annotation</artifactId>",
    "<scope>provided</scope>",
    "<version>%{version}</version>",
    "<release>8</release>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("junit", "SNAPSHOT", "<source>", "<target>", "<parent>", "felix", "maven-bundle-plugin"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/org.osgi.service.component-%{version}.jar --describe-module org.osgi.service.component > module-describe.txt
grep -q '^org.osgi.service.component' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }

%files -f .mfiles
%doc LICENSE
