@echo off
echo Building protobuf-lite.lib using CMake...
cd /d %~dp0

REM Create build directory
if not exist protobuf-build mkdir protobuf-build
cd protobuf-build

REM Configure and build for both architectures
echo Configuring for x64...
cmake -G "Visual Studio 17 2022" -A x64 ^
    -Dprotobuf_BUILD_TESTS=OFF ^
    -Dprotobuf_BUILD_EXAMPLES=OFF ^
    -Dprotobuf_BUILD_PROTOC_BINARIES=OFF ^
    -Dprotobuf_BUILD_SHARED_LIBS=OFF ^
    -Dprotobuf_INSTALL=OFF ^
    -Dprotobuf_WITH_ZLIB=OFF ^
    -Dprotobuf_MSVC_STATIC_RUNTIME=OFF ^
    ../protobuf-source

if errorlevel 1 (
    echo Error: cmake configuration failed
    pause
    exit /b 1
)

echo Building x64 Release...
cmake --build . --config Release --target libprotobuf-lite --parallel

if errorlevel 1 (
    echo Error: x64 build failed
    pause
    exit /b 1
)

REM Copy x64 release lib
copy Release\libprotobuf-lite.lib ..\spt\x64\

echo Building x86 Release...
cmake --build . --config Release --target libprotobuf-lite --parallel -- -p:Platform=Win32

if errorlevel 1 (
    echo Error: x86 build failed
    pause
    exit /b 1
)

REM Copy x86 release lib (if built in separate directory)
if exist "Release\libprotobuf-lite.lib" (
    copy Release\libprotobuf-lite.lib ..\spt\x86\
) else (
    echo Note: x86 version may need separate build directory
)

echo.
echo Build completed!
echo libprotobuf-lite.lib files are in:
echo - spt\x64\libprotobuf-lite.lib
echo - spt\x86\libprotobuf-lite.lib
echo.
pause
