import random


def input_default(prompt, default):
    """
    Prompts you to enter parameters from the command line.

    Arguments:
        prompt  -- the message to prompt
        default -- the default value to use if you do not want to change the parameter
    """
    return input("%s [%s] " % (prompt, default)) or default


def uniform(domain_settings):
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

    if a < 0 or b < 0:
        raise Exception("ERROR: a and b must be positive.")
    elif a > b:
        raise Exception("ERROR: a must be lower than b.")

    print("\nNew a and b")
    print("a: {}".format(a))
    print("b: {}".format(b))

    tmp = 0
    counter = 0
    while counter < 3:
        tmp = random.uniform(a, b)
        if tmp < 100:
            counter += 1
        else:
            break

    if tmp >= 100:
        domain_settings.nodes = int(tmp)
    else:
        print("Unfortunately, the value generated is too small. The number of nodes has been reset to the value {}.".format(domain_settings.nodes))


def triangular(domain_settings):
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

    if low < 0 or high < 0:
        raise Exception("ERROR: low and high must be positive.")
    elif low > high:
        raise Exception("ERROR: low must be lower than high.")

    print("\nNew low and high")
    print("low: {}".format(low))
    print("high: {}".format(high))

    tmp = 0
    counter = 0
    while counter < 3:
        tmp = random.triangular(low, high)
        if tmp < 100:
            counter += 1
        else:
            break

    if tmp >= 100:
        domain_settings.nodes = int(tmp)
    else:
        print("Unfortunately, the value generated is too small. The number of nodes has been reset to the value {}.".format(domain_settings.nodes))


def gauss(domain_settings):
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

    if mu < 0 or sigma < 0:
        raise Exception("ERROR: mu and sigma must be positive.")

    print("\nNew mu and sigma")
    print("mu: {}".format(mu))
    print("sigma: {}".format(sigma))

    tmp = 0
    counter = 0
    while counter < 3:
        tmp = random.gauss(mu, sigma)
        if tmp < 100:
            counter += 1
        else:
            break

    if tmp >= 100:
        domain_settings.nodes = int(tmp)
    else:
        print("Unfortunately, the value generated is too small. The number of nodes has been reset to the value {}.".format(domain_settings.nodes))


def normal(domain_settings):
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

    if mu < 0 or sigma < 0:
        raise Exception("ERROR: mu and sigma must be positive.")

    print("\nNew mu and sigma")
    print("mu: {}".format(mu))
    print("sigma: {}".format(sigma))

    tmp = 0
    counter = 0
    while counter < 3:
        tmp = random.normalvariate(mu, sigma)
        if tmp < 100:
            counter += 1
        else:
            break

    if tmp >= 100:
        domain_settings.nodes = int(tmp)
    else:
        print("Unfortunately, the value generated is too small. The number of nodes has been reset to the value {}.".format(domain_settings.nodes))
