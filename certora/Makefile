default: help

PATCH         = applyHarness.patch
CONTRACTS_DIR = ../contracts
MUNGED_DIR    = ./munged
AMM_origin = ../contracts/AMM.vy
AMM_munged = ./munged/AMM.vy

help:
	@echo "usage:"
	@echo "  make clean:  remove all generated files (those ignored by git)"
	@echo "  make $(MUNGED_DIR): create $(MUNGED_DIR) directory by applying the patch file to $(CONTRACTS_DIR)"
	@echo "  make record: record a new patch file capturing the differences between $(CONTRACTS_DIR) and $(MUNGED_DIR)"

munge:
	cp $(AMM_origin) $(MUNGED_DIR)
	patch -d $(MUNGED_DIR) < $(PATCH)

record:
	diff -burN $(AMM_origin) $(AMM_munged) | sed 's+\$(AMM_origin)/++g' | sed 's+$(AMM_munged)++g' > $(PATCH)
	
clean:
	git clean -fdX
	touch $(PATCH)