.PHONY: bench test report

build:
	virtualenv .
	bin/easy_install funkload

test:
	bin/fl-run-test loadtest.py

bench:
	bin/fl-run-bench loadtest.py MarketplaceTest.test_marketplace

report:
	bin/fl-build-report --html -o html simple-bench.xml
