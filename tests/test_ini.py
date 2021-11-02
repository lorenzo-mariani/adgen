import os

from adgen.utils.loader import check_parameters


def test_parameters():
    # Everything is correct inside correct_config.ini
    path_to_check = os.path.join(os.path.abspath('tests'), 'data', 'correct_config.ini')
    check = check_parameters(path_to_check)
    assert check == 0

    # Some sections are missing
    path_to_check = os.path.join(os.path.abspath('tests'), 'data', 'missing_section.ini')
    check = check_parameters(path_to_check)
    assert check == -1

    # Some sections are incorrect
    path_to_check = os.path.join(os.path.abspath('tests'), 'data', 'wrong_section.ini')
    check = check_parameters(path_to_check)
    assert check == -1

    # Sum of probabilities greater than 100
    path_to_check = os.path.join(os.path.abspath('tests'), 'data', 'wrong_prob.ini')
    check = check_parameters(path_to_check)
    assert check == -2

    # Probability lower than 0
    path_to_check = os.path.join(os.path.abspath('tests'), 'data', 'negative_prob.ini')
    check = check_parameters(path_to_check)
    assert check == -2
