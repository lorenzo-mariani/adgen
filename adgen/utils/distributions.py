import random
import yaml

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
    """
    Checks whether the uniform distribution parameters are valid.

    Arguments:
        a -- first parameter of the distribution
        b -- second parameter of the distribution
    """
    if a < 0 or b < 0:
        raise Exception("ERROR: uniform(a,b): a and b must be positive.")

    elif a > b:
        raise Exception("ERROR: uniform(a,b): a must be lower than b.")


def check_triangular(low, high):
    """
    Checks whether the triangular distribution parameters are valid.

    Arguments:
        low  -- first parameter of the distribution
        high -- second parameter of the distribution
    """
    if low < 0 or high < 0:
        raise Exception("ERROR: triangular(low,high): low and high must be positive.")
    elif low > high:
        raise Exception("ERROR: triangular(low,high): low must be lower than high.")


def check_gauss(mu, sigma):
    """
    Checks whether the gauss distribution parameters are valid.

    Arguments:
        mu    -- first parameter of the distribution
        sigma -- second parameter of the distribution
    """
    if mu < 0 or sigma < 0:
        raise Exception(f"ERROR: gauss(mu,sigma): mu and sigma must be positive.")


def check_gamma(alpha, beta):
    """
    Checks whether the gamma distribution parameters are valid.

    Arguments:
        alpha -- first parameter of the distribution
        beta  -- second parameter of the distribution
    """
    if alpha < 0 or beta < 0:
        raise Exception(f"ERROR: gamma(alpha,beta): alpha and beta must be positive.")


def generate_random_value(domain_settings, distr, val_1, val_2):
    """
    Generates a random value of nodes based on the distribution.
    A maximum of 3 attempts are made; if in 3 attempts you do not
    get a value greater than 100 the value of the nodes to be
    generated will be equal to the default value.

    Arguments:
        domain_settings -- the entity to which to configure the nodes
        distr           -- distribution
        val_1           -- first parameter of the distribution
        val_2           -- second parameter of the distribution
    """
    tmp = 0
    counter = 0

    while counter < 3:
        if distr == "uniform":
            tmp = random.uniform(val_1, val_2)
        elif distr == "triangular":
            tmp = random.triangular(val_1, val_2)
        elif distr == "gauss":
            tmp = random.gauss(val_1, val_2)
        elif distr == "gamma":
            tmp = random.gammavariate(val_1, val_2)

        if tmp < 100:
            counter += 1
        else:
            break

    if tmp <= 0:
        domain_settings.nodes = DEFAULT_DOMAIN_SETTINGS.get('nodes')
        print("Unfortunately, the value generated is lower or equal to zero. The number of nodes has been reset to the value {}.".format(domain_settings.nodes))
    else:
        domain_settings.nodes = int(tmp)


def interactive_uniform(domain_settings):
    """
    This function creates a uniform distribution based on the
    values entered by the user (interactive mode).

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
    values entered by the user (interactive mode).

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
    values entered by the user (interactive mode).

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

    check_gauss(mu, sigma)

    print("\nNew mu and sigma")
    print("mu: {}".format(mu))
    print("sigma: {}".format(sigma))

    generate_random_value(domain_settings, "gauss", mu, sigma)


def interactive_gamma(domain_settings):
    """
    This function creates a Gaussian distribution based on the
    values entered by the user (interactive mode).

    Arguments:
        domain_settings -- the entity to which to configure the domain
    """
    alpha = 100
    beta = 5

    print("Current alpha and beta")
    print("alpha: {}".format(alpha))
    print("beta: {}\n".format(beta))

    alpha = int(input_default("Enter alpha", alpha))
    beta = int(input_default("Enter beta", beta))

    check_gamma(alpha, beta)

    print("\nNew alpha and beta")
    print("alpha: {}".format(alpha))
    print("beta: {}".format(beta))

    generate_random_value(domain_settings, "gamma", alpha, beta)


def run_distributions(args, domain_settings):
    """
    This function creates distributions based on the values
    entered by the user (run mode).

    Arguments:
        args            -- the distribution entered by the user
        domain_settings -- the entity to which to configure the domain
    """
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
    elif distr == "gauss":
        check_gauss(val_1, val_2)
        generate_random_value(domain_settings, distr, val_1, val_2)
    elif distr == "gamma":
        check_gamma(val_1, val_2)
        generate_random_value(domain_settings, distr, val_1, val_2)


def config_distributions(args, domain_settings):
    """
    This function creates distributions based on the values
    entered by the user (config mode).

    Arguments:
        args            -- the distribution entered by the user
        domain_settings -- the entity to which to configure the domain
    """
    path = args

    with open(path) as fh:
        data = yaml.load(fh, Loader=yaml.FullLoader)
        distr = data[0].get('distribution').lower()
        val_1 = data[0].get('x')
        val_2 = data[0].get('y')

        if distr == "uniform":
            check_uniform(val_1, val_2)
            generate_random_value(domain_settings, distr, val_1, val_2)
        elif distr == "triangular":
            check_triangular(val_1, val_2)
            generate_random_value(domain_settings, distr, val_1, val_2)
        elif distr == "gauss":
            check_gauss(val_1, val_2)
            generate_random_value(domain_settings, distr, val_1, val_2)
        elif distr == "gamma":
            check_gamma(val_1, val_2)
            generate_random_value(domain_settings, distr, val_1, val_2)
