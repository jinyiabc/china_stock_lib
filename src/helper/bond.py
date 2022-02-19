import yearfrac as yf
import matplotlib.pyplot as plt
from collections import namedtuple



def time_factors(settlement_date,
                 coupon_schedule,
                 coupon_freq, convention=None):
    """
    This is a function which outputs the time factors for a schedule of
    coupon payments relative to a single settlement date.
    Using 30/360 ISDA day count convention.
    argument:  convention
        Actual/Actual ISDA = 'act_isda'
        Actual/Actual AFB = 'act_afb'
        30E/360 ISDA = 'd30360e'
        30/365 daycount = '30365'
    """
    if convention == None:
        convention = 'act_afb'
    time_factors = []

    if convention == 'd30360e':
        yf0 = yf.d30360e
    elif convention == 'act_afb':
        yf0 = yf.act_afb
    elif convention == 'act_isda':
        yf0 = yf.act_isda
    elif convention == '30365':
        yf0 = yf.d30365

    for dates in coupon_schedule:
        if convention == 'd30360e':
            time_factors.append(yf0(*settlement_date, *dates, matu=False) * coupon_freq)
        else:
            time_factors.append(
                yf0(*settlement_date, *dates) * coupon_freq)  # other than 'd30360e', no argument matu.
    return time_factors

def cash_flows(coupon_schedule,
               coupon_rate,
               coupon_freq,
               face,
               to_maturity=True):
    """
    This a function which models the cash flows amounts of the bond and
    outputs a list of nominal cash flows

    INPUTS:
    #coupon_schedule = the dates of bonds cash flows where the first date
        is the next coupon date and the last is the maturity of the bond

    #coupon_rate = the interest rate paid by the bond, expressed as
        a decimal value

    #coupon_freq =  the number of times per year that the bond
        pays interest

    #face =  the par amount of the bond

    UPDATE
    #to_maturity = Adds the bond principal to the final cash flow, this
        defaults to True.

    OUTPUTS:
    #cf = a list object containing nominal cash flows
    """
    cf = []

    for dates in coupon_schedule:
        cf.append(coupon_rate * face / coupon_freq)

    if to_maturity:
        cf[-1] += face

    return cf




def discount_factors(settlement_date,
                     coupon_schedule,
                     coupon_freq,
                     bond_yld):
    """
    This is a function which calcultes the discount factors which are used to
    bring nominal cash flows back to present value:
    """
    tf = time_factors(settlement_date, coupon_schedule, coupon_freq)
    df = []

    for factors in tf:
        df.append(1 / (1 + bond_yld / coupon_freq) ** factors)
    return df


def present_value(settlement_date,
                  coupon_schedule,
                  coupon_rate,
                  coupon_freq,
                  face,
                  bond_yld):
    """
    This is function which calculates the sum product of the cash_flows
    and discount_factors function outputs
    """

    cf = cash_flows(coupon_schedule, coupon_rate, coupon_freq, face)
    df = discount_factors(settlement_date, coupon_schedule, coupon_freq, bond_yld)

    pv_cf = [cf[i] * df[i]
             for i in range(len(cf))]

    return sum(pv_cf)


def accrued_interest(settlement_date,
                     coupon_schedule,
                     coupon_rate,
                     coupon_freq,
                     face,
                     prev_coupon):
    """
    This is a function which calcultes the accrued interest of the bond.
    Accrured interest is the 'earned' but unpaid interest owed to the
    bond seller on the settlement date.
    """

    full_coupon = coupon_rate * face / coupon_freq
    accrued_days = yf.d30360e(*prev_coupon, *settlement_date, matu=True) * 360
    days_between_coupon = yf.d30360e(*prev_coupon, *coupon_schedule[0], matu=True) * 360
    accrued_interest = full_coupon * accrued_days / days_between_coupon

    if settlement_date == coupon_schedule[0]:
        return full_coupon
    else:
        return accrued_interest


def bond_price(settlement_date,
               coupon_schedule,
               coupon_rate,
               coupon_freq,
               face,
               prev_coupon,
               bond_yld,
               clean=True,
               precision=6):
    """
    This is a function which combines the outputs from the functions:
    present_value and accrued_interest
    to return either the clean or dirty price fo the bond.
    By default the function will return the clean price.
    """

    dirty_px = present_value(settlement_date, coupon_schedule, coupon_rate,
                             coupon_freq, face, bond_yld)

    ai = accrued_interest(settlement_date, coupon_schedule, coupon_rate,
                          coupon_freq, face, prev_coupon)

    if clean:
        return round(dirty_px - ai, precision)
    else:
        return round(dirty_px, precision)


def numerical_derivative(settlement_date,
                         coupon_schedule,
                         coupon_rate,
                         coupon_freq,
                         face,
                         prev_coupon,
                         bond_yld,
                         bump=.0001):
    """
    This function calculates and returns the numerical derivative
    of a bond by bumping and re-pricing it for the given 'bump' level.
    The function uses a bump of 1 basis point by default.

    #INPUTS:
    #settlement_date = Single date value for the date at which the security
        is exchanged for cash, typically T+1 or T+2, iterable containing: YYYY, MM, DD

    #coupon_schedule = The dates of bonds cash flows where the first date is
        the next coupon date and the last is the maturity of the bond

    #coupon_rate = the interest rate paid by the bond, expressed as a decimal value

    #coupon_freq = the number of times per year that the bond pays interest

    #face =  the par amount of the bond

    #bond_yld = The yield at which the bond is being priced

    #prev_coupon =  an iterable that contains the date value, YYYY, MM, DD
        of when the previous coupon was paid

    #OUTPUTS:
    # The slope of the bond price function at the given yield
    """

    bump_price = bond_price(settlement_date,
                            coupon_schedule,
                            coupon_rate,
                            coupon_freq,
                            face,
                            prev_coupon,
                            (bond_yld - bump))

    price = bond_price(settlement_date,
                       coupon_schedule,
                       coupon_rate,
                       coupon_freq,
                       face,
                       prev_coupon,
                       bond_yld)

    numerical_derivative = (price - bump_price) / bump

    return numerical_derivative


def bond_yield(settlement_date,
               coupon_schedule,
               coupon_rate,
               coupon_freq,
               face,
               prev_coupon,
               price,
               precision=6,
               show_stats=False):
    """
    This function calculates and returns the yield of a bond. It has the
    option to display the number of guesses and each respected guessed value.
    By default the guess stats are not show. The user can also select to
    whichlevel of precision in the price difference that the yield should
    be calculated to, default is six.

    #INPUTS:
    #settlement_date = Single date value for the date at which the security
        is exchanged for cash, typically T+1 or T+2, iterable containing: YYYY, MM, DD

    #coupon_schedule = The dates of bonds cash flows where the first date is
        the next coupon date and the last is the maturity of the bond

    #coupon_rate = the interest rate paid by the bond, expressed as a decimal value

    #coupon_freq = the number of times per year that the bond pays interest

    #face =  the par amount of the bond

    #bond_yld = The yield at which the bond is being priced

    #prev_coupon =  an iterable that contains the date value, YYYY, MM, DD
        of when the previous coupon was paid

     OUTPUTS:
    #The yield of the bond. If show_stats is set to True then the number of
    guesses and guess values will also be printed.
    """

    yld = 0  # the first initial guess value
    n = 0  # counter for number of iterations

    # as long as the absolute rounded price difference is greater than zero
    # keep itererating through guesses
    while abs(round(bond_price(settlement_date,
                               coupon_schedule,
                               coupon_rate,
                               coupon_freq,
                               face,
                               prev_coupon,
                               yld,
                               precision=
                               precision) - price, 6)) > 0:

        # incremented for each guess
        n += 1

        # the bond price output using the guessed yield
        estimated_price = bond_price(settlement_date,
                                     coupon_schedule,
                                     coupon_rate,
                                     coupon_freq,
                                     face,
                                     prev_coupon,
                                     yld)

        # the derivative/slope of the bond price function at our guess yield
        derivative = numerical_derivative(settlement_date,
                                          coupon_schedule,
                                          coupon_rate,
                                          coupon_freq,
                                          face,
                                          prev_coupon,
                                          yld)

        # the equation that calculates the next and closer guess input
        yld = yld - (estimated_price - price) / derivative

        # returns a print statement for each guess and it's output
        if show_stats == True:
            print(f"guess{n}: {round(yld, precision) * 100} %")

    # once the absolute rounded price difference is zero
    # we calculate the price at this yield level
    check_price = bond_price(settlement_date,
                             coupon_schedule,
                             coupon_rate,
                             coupon_freq,
                             face,
                             prev_coupon,
                             yld)

    # Summary print statement if user has selected to show stats
    if show_stats == True:

        print(f"This function estimated the bond yield within {precision} decimal places using a total of {n} guesses")

        print(f"The price difference at this yield is : {check_price - price}")

        return yld

    else:

        return yld


def hpr_received_coupons(settlement_date, coupon_schedule, horizon_date):
    """
    This is a function which evaluates which coupon dates will be realised
    in a coupon schedule between a settlement and horizon date.

    INPUTS:
    # settlement_date = Single date value for the date at which the security
        is exchanged for cash, typically T+1 or T+2, iterable containing: YYYY, MM, DD

    # coupon_schedule = The dates of bonds cash flows where the first date is
        the next coupon date and the last is the maturity of the bond

    # horizon_date = Single date value when the bond will be transacted in
        the future

    OUTPUTS:
    # coupon_dates_within_holding_period = an iterable containing realised
        coupon dates
    """
    holding_period = yf.d30360e(*settlement_date, *horizon_date, matu=False)
    coupon_dates_within_holding_period = []

    for dates in coupon_schedule:
        if yf.d30360e(*settlement_date, *dates, matu=False) <= holding_period:
            coupon_dates_within_holding_period.append(dates)

    return coupon_dates_within_holding_period


def hpr_coupon_amounts(settlement_date,
                       coupon_schedule,
                       horizon_date,
                       coupon_rate,
                       coupon_freq,
                       face):
    """
    This is a function which calculates the coupon amounts for realised coupons
        during the holding period.

    INPUTS:
    # settlement_date = Single date value for the date at which the security
        is exchanged for cash, typically T+1 or T+2, iterable containing: YYYY, MM, DD

    # coupon_schedule = The dates of bonds cash flows where the first date is
        the next coupon date and the last is the maturity of the bond

    # horizon_date = Single date value when the bond will be transacted in
        the future

    # coupon_rate = the interest rate paid by the bond, expressed as a decimal value

    # coupon_freq = the number of times per year that the bond pays interest

    # face =  the par amount of the bond

    OUTPUTS:
    # cf = an iterable containing realised coupon amounts
    """

    coupon_dates_within_holding_period = hpr_received_coupons(settlement_date,
                                                              coupon_schedule,
                                                              horizon_date)

    cf = cash_flows(coupon_dates_within_holding_period,
                    coupon_rate,
                    coupon_freq,
                    face,
                    to_maturity=False)

    return cf


def hpr_coupon_horizon_value(settlement_date,
                             coupon_schedule,
                             horizon_date,
                             coupon_rate,
                             coupon_freq,
                             face,
                             reinvestment_rate):
    """
    This is a function which calculates the future value of realised coupons
    at the horizon date and sums them.

    INPUTS:
    # settlement_date = Single date value for the date at which the security
        is exchanged for cash, typically T+1 or T+2, iterable containing: YYYY, MM, DD

    # coupon_schedule = The dates of bonds cash flows where the first date is
        the next coupon date and the last is the maturity of the bond

    # horizon_date = Single date value when the bond will be transacted in
        the future

    # coupon_rate = the interest rate paid by the bond, expressed as a decimal value

    # coupon_freq = the number of times per year that the bond pays interest

    # face =  the par amount of the bond

    # reinvestment_rate = the discount rate used to calculate future value
        of realised coupons

    OUTPUTS:
    # sum(fv_coupon) = the sum of future value of realised coupons
    """

    # a list to contain the time between each coupon date and the horizon date
    investment_periods = []

    # calculation of each time period
    for dates in hpr_received_coupons(settlement_date, coupon_schedule, horizon_date):
        investment_periods.append(yf.d30360e(*dates, *horizon_date, matu=False))

    # a list containing the discount factor for each coupon
    df = []

    # calculation of each discount factor
    for periods in investment_periods:
        df.append((1 + reinvestment_rate / coupon_freq) ** (periods * coupon_freq))

    # a function that generates a list containing each coupon amount
    cf = hpr_coupon_amounts(settlement_date,
                            coupon_schedule,
                            horizon_date,
                            coupon_rate,
                            coupon_freq,
                            face)

    # a lit comprehension that contains the future value of each coupon
    fv_coupon = [df[i] * cf[i] for i in range(len(cf))]

    # return value is the total sum of all coupon future values
    return sum(fv_coupon)


def hpr_horizon_bond_price(settlement_date,
                           horizon_date,
                           coupon_schedule,
                           coupon_rate,
                           coupon_freq,
                           face,
                           prev_coupon,
                           bond_horizon_yld,
                           clean=True,
                           precision=6):
    """
    This is a function which calculates the price of a bond at a future date, the horizon date.

    #INPUTS:
    # settlement_date = Single date value for the date at which the security
        is exchanged for cash, typically T+1 or T+2, iterable containing: YYYY, MM, DD

    # horizon_date = Single date value when the bond will be transacted in
        the future

    # coupon_schedule = The dates of bonds cash flows where the first date is
        the next coupon date and the last is the maturity of the bond

    # coupon_rate = the interest rate paid by the bond, expressed as a decimal value

    # coupon_freq = the number of times per year that the bond pays interest

    # face =  the par amount of the bond

    # prev_coupon =  an iterable that contains the date value, YYYY, MM, DD
        of when the previous coupon was paid

    # bond_horizon_yld = The yield at which the bond is being priced at the horizon date

    #clean = Boolean which defaults to True. When True the function returns
        the clean price of the bond, False it returns the dirty price of the bond.

    # precision = The number of decimals that the bond price will be calculated to,
        defaults to six

    OUTPUTS:
    #The price of the bond at the horizon date, in clean or dirty terms
        dependent on the function inputs.
    """

    # Generate a list containing the received coupons
    received_coupons = hpr_received_coupons(settlement_date, coupon_schedule, horizon_date)

    # Remove the recevied coupons from the coupon schedule
    remaining_coupons = [date for date in coupon_schedule
                         if date not in received_coupons]

    # Use the latest received coupon as the previous coupon date
    prev_coupon = received_coupons[-1]

    # Bond price calculated on the horizon date using the adjusted coupon schedule
    dirty_px = present_value(horizon_date, remaining_coupons, coupon_rate,
                             coupon_freq, face, bond_horizon_yld)

    # Accrued interest calculated as of the horizon date using the adjusted coupon schedule
    ai = accrued_interest(horizon_date, remaining_coupons, coupon_rate,
                          coupon_freq, face, prev_coupon)

    if clean:
        return round(dirty_px - ai, precision)
    else:
        return round(dirty_px, precision)


def hpr_total_future_value(settlement_date,
                           horizon_date,
                           coupon_schedule,
                           coupon_rate,
                           coupon_freq,
                           face,
                           prev_coupon,
                           bond_horizon_yld,
                           reinvestment_rate):
    """
    This is a function which combines the output from the bond_price_at_horizon_date
        and hpr_coupon_horizon_value to calculate the total future value of the bond
        at the horizon date.

    #INPUTS:
    # settlement_date = Single date value for the date at which the security
        is exchanged for cash, typically T+1 or T+2, iterable containing: YYYY, MM, DD

    # horizon_date = Single date value when the bond will be transacted in
        the future

    # coupon_schedule = The dates of bonds cash flows where the first date is
        the next coupon date and the last is the maturity of the bond

    # coupon_rate = the interest rate paid by the bond, expressed as a decimal value

    # coupon_freq = the number of times per year that the bond pays interest

    # face =  the par amount of the bond

    # prev_coupon =  an iterable that contains the date value, YYYY, MM, DD
        of when the previous coupon was paid

    # bond_horizon_yld = The yield at which the bond is being priced at the horizon date

    # reinvestment_rate = the discount rate used to calculate future value
        of realised coupons

    OUTPUTS:
    # The total future value of the bond, including reinvested coupons
    """

    bond_price_at_horizon_date = hpr_horizon_bond_price(
        settlement_date,
        horizon_date,
        coupon_schedule,
        coupon_rate,
        coupon_freq,
        face,
        prev_coupon,
        bond_horizon_yld)

    reinvested_coupons = hpr_coupon_horizon_value(settlement_date,
                                                  coupon_schedule,
                                                  horizon_date,
                                                  coupon_rate,
                                                  coupon_freq,
                                                  face,
                                                  reinvestment_rate)

    return bond_price_at_horizon_date + reinvested_coupons


def hpr_return(settlement_date,
               horizon_date,
               coupon_schedule,
               coupon_rate,
               coupon_freq,
               face,
               prev_coupon,
               bond_settle_yld,
               bond_horizon_yld,
               reinvestment_rate,
               return_hpr=False):
    """
    This is a function which calculates the total future value of the bond and the
    present value of the bond. It then evaluates the percentage change from present
    value to future value which is then annualised. The function also has the option
    to return the holding period return (non-annualised return).

    #INPUTS:
    # settlement_date = Single date value for the date at which the security
        is exchanged for cash, typically T+1 or T+2, iterable containing: YYYY, MM, DD

    # horizon_date = Single date value when the bond will be transacted in
        the future

    # coupon_schedule = The dates of bonds cash flows where the first date is
        the next coupon date and the last is the maturity of the bond

    # coupon_rate = the interest rate paid by the bond, expressed as a decimal value

    # coupon_freq = the number of times per year that the bond pays interest

    # face =  the par amount of the bond

    # prev_coupon =  an iterable that contains the date value, YYYY, MM, DD
        of when the previous coupon was paid

    # bond_settle_yld = The yield at which the bond is traded on the settlement day

    # bond_horizon_yld = The yield at which the bond is being priced at the horizon date

    # reinvestment_rate = the discount rate used to calculate future value
        of realised coupons

    # return_hpr = Boolean that defaults to False. If set to True the function
        will return the holding period return instead of the annualised return

    OUTPUTS:

    # The annualised return or holding period return of the bond for the holding
        period for the given settlement yield horizon yield and reinvestment rate.
    """

    fv = hpr_total_future_value(settlement_date,
                                horizon_date,
                                coupon_schedule,
                                coupon_rate,
                                coupon_freq,
                                face,
                                prev_coupon,
                                bond_horizon_yld,
                                reinvestment_rate)

    pv = bond_price(settlement_date,
                    coupon_schedule,
                    coupon_rate,
                    coupon_freq,
                    face,
                    prev_coupon,
                    bond_settle_yld)

    holding_period_return = fv / pv - 1

    if return_hpr:
        return holding_period_return

    holding_period = yf.d30360e(*settlement_date, *horizon_date, matu=True)

    annualised_return = (1 + holding_period_return) ** (1 / holding_period) - 1

    return annualised_return


if __name__ == '__main__':
    # The observed market value of the bond that we are calculating the yield for
    price = 112.637

    # NOTICE: Bond yield and name is no longer an entry.
    Bond_Data = namedtuple("Bond_Data",
                           """ 
                           coupon_schedule, 
                           coupon_rate, 
                           coupon_freq, 
                           face,  
                           prev_coupon""")

    corp_5_2026_coupon_schedule = [(2022, 9, 1),
                                   (2023, 9, 1),
                                   (2024, 9, 1),
                                   (2025, 9, 1),
                                   (2026, 9, 1)]

    corp_5_2026 = Bond_Data(corp_5_2026_coupon_schedule,
                            0.05,
                            1,
                            100,
                            (2021, 9, 1))

    settlement_date = (2021, 9, 1)

    bond_yield(settlement_date, *corp_5_2026, price, precision=12, show_stats=True)



