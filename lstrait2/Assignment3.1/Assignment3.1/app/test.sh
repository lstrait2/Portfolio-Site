# test script to run all tests
# use chmod u+x test.sh if unable to run
echo ""
echo "Running Portfolio Tests"
echo ""
python portfolio_tests.py
echo ""
echo "Running Parser Tests"
echo ""
python xml_parser_tests.py
echo ""
echo "Running db Tests"
echo ""
python db_tests.py
