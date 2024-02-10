class PriceNotificationsChecker:
    def __init__(self):
        self.threshold = 4.0

    @staticmethod
    def _get_latest_price_change(prices):
        current_price = prices[-1]
        prev_price = prices[-2]

        price_change = (current_price - prev_price) * 100 / prev_price

        return price_change

    def has_fallen_below_threshold(self, prices):
        price_change = self._get_latest_price_change(prices)

        if price_change <= -1 * self.threshold:
            return True, price_change
        else:
            return False, None

    def has_risen_above_threshold(self, prices):
        price_change = self._get_latest_price_change(prices)

        if price_change >= self.threshold:
            return True, price_change
        else:
            return False, None

    @staticmethod
    def rising_days(prices):
        num_of_days = 0
        idx = len(prices) - 1

        increment = 1

        while increment > 0 and idx >= 1:
            increment = prices[idx] - prices[idx - 1]

            if increment > 0:
                num_of_days += 1
                idx -= 1

        total_percentage_increment = (prices[len(prices) - 1] - prices[len(prices) - 1 - num_of_days]) * 100 / prices[len(prices) - 1 - num_of_days]

        return num_of_days, total_percentage_increment

    @staticmethod
    def falling_days(prices):
        num_of_days = 0
        idx = len(prices) - 1

        increment = -1

        while increment < 0 and idx >= 1:
            increment = prices[idx] - prices[idx - 1]

            if increment < 0:
                num_of_days += 1
                idx -= 1

        total_percentage_increment = (prices[len(prices) - 1] - prices[len(prices) - 1 - num_of_days]) * 100 / prices[len(prices) - 1 - num_of_days]

        return num_of_days, total_percentage_increment
