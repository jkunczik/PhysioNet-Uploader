# PhysioNet-Uploader
A CLI tool utilizing Python and Selenium to programmatically upload a dataset to PhysioNet.

The new Version of PhysioNet does not allow to upload and extract a ZIP file of your dataset, nor does it offer a programatic way to upload your data (at least that I know of). Hence, I wrote a litte python script, which automatically uploads a dataset using selenium browser automation.

## Reqiurements
- conda
- Firefox

## How to use
Simply run the command:

```bash
pnetu --ProjectID {ID of your project} \
      --Username {PhysioNet username} \
      --Password {PhysioNet password} \
      --DatsetDir {Dataset directory to upload}
```
During the scripts first execution it will install the needed conda environment. Hence, it will take a moment longer. 

If you don't want to paste your credentials into the command line, you can also add all parameters to a .conf or .yaml config file in the scripts root directory.

## Disclaimer
The script is provided "as is". I am not planning to maintain this repository on a regular basis. Any update of the PhysioNet Web UI may break this script. Nevertheless, I hope that it helps somebody.


