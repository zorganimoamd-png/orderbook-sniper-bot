from datetime import datetime, timezone

class MarketHoursFilter:
    """
    صمام أمان ساعات عمل الأسواق المالية (الذهب والفوركس):
    يمنع إرسال أي إشارة أو تحليل أثناء إغلاق عطلة نهاية الأسبوع (السبت والأحد).
    """

    @staticmethod
    def is_market_open() -> bool:
        """
        التحقق مما إذا كان سوق الذهب والفوركس مفتوحاً الآن بتوقيت غرينتش (UTC)
        """
        now = datetime.now(timezone.utc)
        weekday = now.weekday()  # Monday is 0, Sunday is 6
        hour = now.hour

        # 1. يوم السبت (Weekday = 5): السوق مغلق تماماً طوال الـ 24 ساعة
        if weekday == 5:
            return False

        # 2. يوم الجمعة (Weekday = 4): يغلق السوق الساعة 22:00 UTC
        if weekday == 4 and hour >= 22:
            return False

        # 3. يوم الأحد (Weekday = 6): السوق مغلق حتى الساعة 22:00 UTC (افتتاح جلسة أستراليا/آسيا)
        if weekday == 6 and hour < 22:
            return False

        # في باقي الأوقات (من ليل الأحد حتى ليل الجمعة) السوق مفتوح رسمياً
        return True
