D2_DIR := d2
OUT_DIR := out

D2_FILES := $(wildcard $(D2_DIR)/*.d2)

.PHONY: all clean watch list

all:
	@if [ -z "$(D2_FILES)" ]; then \
		echo "No .d2 files found in $(D2_DIR)/"; \
		echo "Create one first (example: d2/flow.d2)"; \
		exit 1; \
	fi
	@mkdir -p $(OUT_DIR)
	@for f in $(D2_FILES); do \
		name=$$(basename $$f .d2); \
		./scripts/render.sh $$f $$name; \
	done

clean:
	rm -rf $(OUT_DIR)

list:
	@echo "D2 files:" $(D2_FILES)

watch:
	fswatch -o $(D2_DIR) | while read; do make -s all; done