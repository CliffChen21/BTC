from abc import ABC, abstractmethod
from math import exp, log, sqrt

from scipy.stats import norm


class EuropeanOption(ABC):
    def __init__(self, S, K, r, sigma, q, tau):
        self.S = S
        self.K = K
        self.r = r
        self.sigma = sigma
        self.q = q
        self.tau = tau

    def d1(self):
        S, K, r, sigma, q, tau = self.S, self.K, self.r, self.sigma, self.q, self.tau
        return (log(S / K) + (r - q + 0.5 * sigma ** 2) * tau) / (sigma * sqrt(tau))

    def d2(self):
        sigma, tau = self.sigma, self.tau
        return self.d1() - sigma * sqrt(tau)

    @abstractmethod
    def delta(self):
        raise NotImplemented

    def gamma(self):
        S, sigma, tau = self.S, self.sigma, self.tau
        return norm.pdf(self.d1()) / (S * sigma * sqrt(tau))

    def vega(self):
        S, tau = self.S, self.tau
        return S * norm.pdf(self.d1()) * sqrt(tau)

    @abstractmethod
    def theta(self):
        raise NotImplemented

    @abstractmethod
    def rho(self):
        raise NotImplemented


class EuropeanCall(EuropeanOption, ABC):

    def __init__(self, S, K, r, sigma, q, tau):
        EuropeanOption.__init__(self, S, K, r, sigma, q, tau)

    def delta(self):
        return norm.cdf(self.d1())

    def theta(self):
        S, K, r, sigma, q, tau = self.S, self.K, self.r, self.sigma, self.q, self.tau
        return -S * norm.pdf(self.d1()) * sigma / 2 / sqrt(tau) - r * K * exp(-r * tau) * norm.cdf(self.d2())

    def rho(self):
        S, K, r, sigma, q, tau = self.S, self.K, self.r, self.sigma, self.q, self.tau
        return K * tau * exp(-r * tau) * norm.cdf(self.d2())


if __name__ == "__main__":
    S = 100
    K = 100
    sigma = 0.2
    r = 0.05
    tau = 91 / 365
    q = 0
    call_option = EuropeanCall(S, K, r, sigma, q, tau)
    print(call_option.delta())
