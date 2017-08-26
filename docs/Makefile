# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = ConcepttoClinic
SOURCEDIR     = .
BUILDDIR      = _build
APIDOCDIR_INTERFACE    = _apidoc_interface
APIDOCDIR_PREDICTION   = _apidoc_prediction
SPHINXAPIDOC  = sphinx-apidoc
PROJDIR       = ../

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: html
html:
	$(SPHINXAPIDOC) -f -o $(APIDOCDIR_INTERFACE)/ $(PROJDIR)/interface/
	$(SPHINXAPIDOC) -f -o $(APIDOCDIR_PREDICTION)/ $(PROJDIR)/prediction/
	@echo
	@echo "apidoc build finished. The api source files are in $(APIDOCDIR)/"
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Sphinx build finished. The build files are in $(BUILDDIR)/"
