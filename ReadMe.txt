az webapp deploy --resource-group RG_Test --name MyWebAppTest --src-path /Users/maec-inflow/Downloads/MyPython/MyPython.zip --type zip





brew  install --cask azure-cli-preview
brew install python@314
brew link --overwrite python@3.14
az --version




brew update && brew install azure-cli
sudo xcode-select --install
brew tap azure/azd && brew install azd
brew install python@314
brew link --overwrite python@3.14

brew trust azure/azure-cli  
brew  trust --cask azure-cli-preview
brew  install --cask azure-cli-preview   ------>>> important
az login
az account show
az --version


pip list
pip list > requirements.txt
pip freeze > requirements.txt

zipinfo MyPython.zip

python3 -m venv venv
source venv/bin/activate


brew list --version python

