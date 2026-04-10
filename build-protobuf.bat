@echo off
echo Building protobuf-lite.lib for x64 and x86...
cd /d %~dp0

REM Set Visual Studio environment
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64
if errorlevel 1 (
    echo Error: Could not find Visual Studio 2019 BuildTools
    pause
    exit /b 1
)

REM Create build directories
if not exist build-x64 mkdir build-x64
if not exist build-x86 mkdir build-x86

REM Build x64 version
echo Building x64 version...
cd build-x64
cmake -G "Visual Studio 16 2019" -A x64 ^
    -Dprotobuf_BUILD_TESTS=OFF ^
    -Dprotobuf_BUILD_EXAMPLES=OFF ^
    -Dprotobuf_BUILD_PROTOC_BINARIES=OFF ^
    -Dprotobuf_BUILD_SHARED_LIBS=OFF ^
    -Dprotobuf_INSTALL=OFF ^
    -Dprotobuf_WITH_ZLIB=OFF ^
    -Dprotobuf_MSVC_STATIC_RUNTIME=OFF ^
    ../protobuf-source/cmake

if errorlevel 1 (
    echo Error: cmake configuration failed for x64
    pause
    exit /b 1
)

msbuild protobuf.sln /p:Configuration=Release /p:Platform=x64 /m
if errorlevel 1 (
    echo Error: Build failed for x64
    pause
    exit /b 1
)

REM Copy x64 lib files
copy Release\libprotobuf-lite.lib ..\spt\x64\
echo x64 libprotobuf-lite.lib built successfully

cd ..

REM Build x86 version
echo Building x86 version...
cd build-x86
cmake -G "Visual Studio 16 2019" -A Win32 ^
    -Dprotobuf_BUILD_TESTS=OFF ^
    -Dprotobuf_BUILD_EXAMPLES=OFF ^
    -Dprotobuf_BUILD_PROTOC_BINARIES=OFF ^
    -Dprotobuf_BUILD_SHARED_LIBS=OFF ^
    -Dprotobuf_INSTALL=OFF ^
    -Dprotobuf_WITH_ZLIB=OFF ^
    -Dprotobuf_MSVC_STATIC_RUNTIME=OFF ^
    ../protobuf-source/cmake

if errorlevel 1 (
    echo Error: cmake configuration failed for x86
    pause
    exit /b 1
)

msbuild protobuf.sln /p:Configuration=Release /p:Platform=Win32 /m
if errorlevel 1 (
    echo Error: Build failed for x86
    pause
    exit /b 1
)

REM Copy x86 lib files
copy Release\libprotobuf-lite.lib ..\spt\x86\
echo x86 libprotobuf-lite.lib built successfully

cd ..

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo New lib files:
echo - spt\x64\libprotobuf-lite.lib
echo - spt\x86\libprotobuf-lite.lib
echo.
pause
