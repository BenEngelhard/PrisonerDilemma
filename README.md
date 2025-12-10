# PrisonerDilemma
The application
# How to work with these two repos?
1. Cloning the main repo with submodules:
git clone --recurse-submodules https://github.com/BenEngelhard/PrisonerDilemma.git

2. Or if already cloned without submodules
git submodule update --init --recursive

3. Synchronizing the main repo with the submodule changes
After pushing submodule changes, go back to the main repo root and update the submodule pointer
git add infrastructure
git commit -m "Update infrastructure version"
git push

# Always update submodules after cloning or pulling
