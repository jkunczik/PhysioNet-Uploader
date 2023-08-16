@ECHO OFF

set call_dir=%CD%
set conda_avail=true
pushd %~dp0

:: Test if conda is available
WHERE conda.exe >nul 2>nul
if %ERRORLEVEL% NEQ 0  (
	echo conda not found. Please install it and try again.
	exit 1
) 

call conda activate Selenium  >nul 2>nul
if %ERRORLEVEL% NEQ 0  (
	:: Install or update the documentation environment
	conda env update -f environment.yml
	timeout 1
	call conda activate Selenium  >nul 2>nul
	if %ERRORLEVEL% NEQ 0  (
		echo ERROR: Could not activate environment.
		exit 1
	) 
) 
python main.py %*
call conda deactivate
goto end

:end
popd