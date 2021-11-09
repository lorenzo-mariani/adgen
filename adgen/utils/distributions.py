import random

from adgen.default_config import DEFAULT_DOMAIN_SETTINGS


def input_default(prompt, default):
    """
    Prompts you to enter parameters from the command line.

    Arguments:
        prompt  -- the message to prompt
        default -- the default value to use if you do not want to change the parameter
    """
    return input("%s [%s] " % (prompt, default)) or default


def check_uniform(a, b):
    if a < 0 or b < 0:
        raise Exception("ERROR: uniform(a,b): a and b must be positive.")
    elif a > b:
        raise Exception("ERROR: uniform(a,b): a must be lower than b.")


def check_triangular(low, high):
    if low < 0 or high < 0:
        raise Exception("ERROR: triangular(low,high): low and high must be positive.")
    elif low > high:
        raise Exception("ERROR: triangular(low,high): low must be lower than high.")


def check_gauss_normal(distr, mu, sigma):
    if mu < 0 or sigma < 0:
        raise Exception(f"ERROR: {distr}(mu,sigma): mu and sigma must be positive.")


def generate_random_value(domain_settings, distr, val_1, val_2):
    tmp = 0
    counter = 0

    while counter < 3:
        if distr == "uniform":
            tmp = random.uniform(val_1, val_2)
        elif distr == "triangular":
            tmp = random.triangular(val_1, val_2)
        elif distr == "gauss":
            tmp = random.gauss(val_1, val_2)
        elif distr == "normal":
            tmp = random.normalvariate(val_1, val_2)

        if tmp < 100:
            counter += 1
        else:
            break

    if tmp >= 100:
        domain_settings.nodes = int(tmp)
    else:
        domain_settings.nodes = DEFAULT_DOMAIN_SETTINGS.get('nodes')
        print("Unfortunately, the value generated is too small. The number of nodes has been reset to the value {}.".format(domain_settings.nodes))


def interactive_uniform(domain_settings):
    """
    This function creates a uniform distribution based on the
    values entered by the user.

    Arguments:
        domain_settings -- the entity to which to configure the domain
    """
    a = 100
    b = 300

    print("Current a and b")
    print("a: {}".format(a))
    print("b: {}\n".format(b))

    a = int(input_default("Enter a", a))
    b = int(input_default("Enter b", b))

    check_uniform(a, b)

    print("\nNew a and b")
    print("a: {}".format(a))
    print("b: {}".format(b))

    generate_random_value(domain_settings, "uniform", a, b)


def interactive_triangular(domain_settings):
    """
    This function creates a triangular distribution based on the
    values entered by the user.

    Arguments:
        domain_settings -- the entity to which to configure the domain
    """
    low = 100
    high = 300

    print("Current low and high")
    print("low: {}".format(low))
    print("high: {}\n".format(high))

    low = int(input_default("Enter low", low))
    high = int(input_default("Enter high", high))

    check_triangular(low, high)

    print("\nNew low and high")
    print("low: {}".format(low))
    print("high: {}".format(high))

    generate_random_value(domain_settings, "triangular", low, high)


def interactive_gauss(domain_settings):
    """
    This function creates a Gaussian distribution based on the
    values entered by the user.

    Arguments:
        domain_settings -- the entity to which to configure the domain
    """
    mu = 100
    sigma = 300

    print("Current mu and sigma")
    print("mu: {}".format(mu))
    print("sigma: {}\n".format(sigma))

    mu = int(input_default("Enter mu", mu))
    sigma = int(input_default("Enter sigma", sigma))

    check_gauss_normal("gauss", mu, sigma)

    print("\nNew mu and sigma")
    print("mu: {}".format(mu))
    print("sigma: {}".format(sigma))

    generate_random_value(domain_settings, "gauss", mu, sigma)


def interactive_normal(domain_settings):
    """
    This function creates a normal distribution based on the
    values entered by the user.

    Arguments:
        domain_settings -- the entity to which to configure the domain
    """
    mu = 100
    sigma = 300

    print("Current mu and sigma")
    print("mu: {}".format(mu))
    print("sigma: {}\n".format(sigma))

    mu = int(input_default("Enter mu", mu))
    sigma = int(input_default("Enter sigma", sigma))

    check_gauss_normal("normal", mu, sigma)

    print("\nNew mu and sigma")
    print("mu: {}".format(mu))
    print("sigma: {}".format(sigma))

    generate_random_value(domain_settings, "normal", mu, sigma)


def run_distributions(args, domain_settings):
    txt = args.split("(")

    distr = txt[0].lower()

    values = txt[1].replace(")", "").replace(" ", "").split(",")
    val_1 = int(values[0])
    val_2 = int(values[1])

    if distr == "uniform":
        check_uniform(val_1, val_2)
        generate_random_value(domain_settings, distr, val_1, val_2)
    elif distr == "triangular":
        check_triangular(val_1, val_2)
        generate_random_value(domain_settings, distr, val_1, val_2)
    elif distr == "gauss" or distr == "normal":
        check_gauss_normal(distr, val_1, val_2)
        generate_random_value(domain_settings, distr, val_1, val_2)
