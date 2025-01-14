# بازی تخته نرد

این پروژه شامل سه کلاس اصلی `routers` ، `server` و `client` به علاوه کلاس `Backgammon_Game` است که برای ایجاد یک ارتباط شبکه‌ای ساده برای بازی تخته نرد طراحی شده‌اند. سرور به عنوان مرکز ارتباطات عمل می‌کند و کلاینت ها از طریق روتر ها می‌توانند با آن ارتباط برقرار کنند.

## ساختار پروژه

### کلاس server

کلاس `server` مسئول مدیریت ارتباطات و پردازش پیام‌ها از کلاینت‌ها است. این کلاس شامل متدهای زیر می‌باشد:

#### ۱. `__init__(self, addr)`

- **شرح**: سازنده کلاس که آدرس سرور را تنظیم می‌کند.
- **ورودی‌ها**:
  - `addr`: آدرس و پورت سرور (مثال: `("127.0.0.1", 9999)`).
- **عملکرد**: متغیرهای اولیه مانند آدرس سرور، اتصال، مجموعه کلاینت‌ها و کلیدهای رمزنگاری را تنظیم می‌کند.

#### ۲. `receive_message(self, conn, addr)`

- **شرح**: متدی برای دریافت و پردازش پیام‌ها از کلاینت‌ها.
- **ورودی‌ها**:
  - `conn`: اتصال کلاینت.
  - `addr`: آدرس کلاینت.
- **عملکرد**:
  - پیام‌های دریافتی را تجزیه و تحلیل کرده و بر اساس نوع دستور (ADD، REMOVE، GET_CLIENTS، DICE) اقدام می‌کند.
  - در صورت دریافت دستور `ADD`، آدرس کلاینت را به مجموعه کلاینت‌ها اضافه می‌کند.
  - در صورت دریافت دستور `REMOVE`، آدرس کلاینت را از مجموعه حذف می‌کند.
  - در صورت دریافت دستور `GET_CLIENTS`، لیست کلاینت‌های آنلاین را به کلاینت ارسال می‌کند.
  - در صورت دریافت دستور `DICE`، دو عدد تصادفی بین ۱ تا ۶ تولید کرده و به کلاینت ارسال می‌کند.

#### ۳. `generate_keys(self, num_keys)`

- **شرح**: متدی برای تولید کلیدهای رمزنگاری.
- **ورودی‌ها**:
  - `num_keys`: تعداد کلیدهایی که باید تولید شود.
- **عملکرد**: کلیدهای رمزنگاری با استفاده از `Fernet` تولید کرده و در یک لیست برمی‌گرداند.

#### ۴. `start_packet_capture(self)`

- **شرح**: متدی برای ضبط بسته‌های شبکه‌ای.
- **عملکرد**:
  - از کتابخانه `pyshark` برای ضبط ترافیک شبکه استفاده می‌کند.
  - بسته‌های دریافتی را تجزیه و تحلیل کرده و محتوای آن‌ها را در یک فایل لاگ ذخیره می‌کند.
  - اطلاعاتی از جمله محتوای بسته، پورت منبع و مقصد را ثبت می‌کند.

#### ۵. `start(self)`

- **شرح**: متدی برای شروع گوش دادن به اتصالات ورودی.
- **عملکرد**:
  - یک سوکت جدید ایجاد کرده و آن را به آدرس مشخص شده متصل می‌کند.
  - در حلقه‌ای بی‌پایان منتظر اتصالات ورودی می‌ماند و برای هر اتصال جدید یک رشته جداگانه برای دریافت پیام‌ها ایجاد می‌کند.
  - همچنین ضبط ترافیک شبکه را در یک رشته جداگانه شروع می‌کند.
  - کلیدهای رمزنگاری تولید شده را به کلاینت ارسال می‌کند.

---

### کلاس routers

کلاس `routers` مسئول مدیریت ارتباطات با همسایگان و کلاینت‌ها است. این کلاس شامل متدهای زیر می‌باشد:

#### ۱. `__init__(self, id, address, neighbors_addresses)`

- **شرح**: سازنده کلاس که شناسه، آدرس و آدرس‌های همسایگان را تنظیم می‌کند.
- **ورودی‌ها**:
  - `id`: شناسه روتر (مثال: "R1").
  - `address`: آدرس و پورت روتر.
  - `neighbors_addresses`: لیستی از آدرس‌های همسایگان.
- **عملکرد**: متغیرهای اولیه مانند آدرس‌ها و اتصالات همسایگان را تنظیم می‌کند.

#### ۲. `send_to_server(self, conn, addr)`

- **شرح**: متدی برای ارسال پیام‌ها به سرور.
- **ورودی‌ها**:
  - `conn`: اتصال به کلاینت.
  - `addr`: آدرس کلاینت.
- **عملکرد**: پیام‌های دریافتی را با استفاده از کلید خصوصی خود روتر رمزگشایی کرده و به همسایگان ارسال می‌کند.

#### ۳. `receive_from_a_neighbor(self, ngh_conn, ngh_addr)`

- **شرح**: متدی برای دریافت پیام‌ها از همسایگان.
- **ورودی‌ها**:
  - `ngh_conn`: اتصال به همسایه.
  - `ngh_addr`: آدرس همسایه.
- **عملکرد**: پیام‌های دریافتی را پردازش کرده و در صورت نیاز کلید رمزنگاری را تنظیم می‌کند.

#### ۴. `send_to_neighbors(self, msg)`

- **شرح**: متدی برای ارسال پیام به تمامی همسایگان.
- **ورودی‌ها**:
  - `msg`: پیام مورد نظر برای ارسال.
- **عملکرد**: پیام را به تمامی همسایگان ارسال می‌کند.

#### ۵. `send_to_client(self, msg)`

- **شرح**: متدی برای ارسال پیام به یک کلاینت خاص.
- **ورودی‌ها**:
  - `msg`: پیام مورد نظر برای ارسال.
- **عملکرد**: پیام را به آدرس مشخص شده ارسال می‌کند.

#### ۶. `connect_to_neighbors(self)`

- **شرح**: متدی برای اتصال به همسایگان.
- **عملکرد**: سوکت‌های لازم برای اتصال به همسایگان را ایجاد کرده و شروع به دریافت پیام‌ها می‌کند.

#### ۷. `start_packet_capture(self)`

- **شرح**: متدی برای ضبط بسته‌های شبکه‌ای.
- **عملکرد**:
  - از کتابخانه `pyshark` برای ضبط ترافیک شبکه استفاده می‌کند.
  - بسته‌های دریافتی را تجزیه و تحلیل کرده و محتوای آن‌ها را در یک فایل لاگ ذخیره می‌کند.

#### ۸. `start(self)`

- **شرح**: متدی برای شروع عملکرد روتر.
- **عملکرد**:
  - اتصال به همسایگان را برقرار کرده و شروع به گوش دادن به اتصالات ورودی می‌کند.
  - همچنین ضبط ترافیک شبکه را در یک رشته جداگانه شروع می‌کند.

---

### کلاس client

کلاس `client` مسئول مدیریت ارتباطات با سرور و همتایان است. این کلاس شامل متدهای زیر می‌باشد:

#### ۱. `__init__(self, server_addr)`

- **شرح**: سازنده کلاس که آدرس سرور را تنظیم می‌کند.
- **ورودی‌ها**:
  - `server_addr`: آدرس سرور.
- **عملکرد**: متغیرهای اولیه شامل آدرس‌های بازی و همتایان را تنظیم می‌کند.

#### ۲. `run_game(self, color)`

- **شرح**: متدی برای راه‌اندازی بازی در یک رشته جداگانه.
- **ورودی‌ها**:
  - `color`: رنگ بازیکن (سفید یا سیاه).
- **عملکرد**: یک شیء از کلاس `Player` ایجاد کرده و بازی را شروع می‌کند.

#### ۳. `send_message(self, conn, msg)`

- **شرح**: متدی برای ارسال پیام به سرور یا همتایان.
- **ورودی‌ها**:
  - `conn`: اتصال به سرور یا همتا.
  - `msg`: پیام مورد نظر برای ارسال.
- **عملکرد**: پیام را رمزنگاری کرده و ارسال می‌کند.

#### ۴. `encrypt_data(self, encrypted_data)`

- **شرح**: متدی برای رمزنگاری داده‌ها.
- **ورودی‌ها**:
  - `encrypted_data`: داده‌های ورودی برای رمزنگاری.
- **عملکرد**: داده‌ها را با استفاده از کلیدهای موجود سه بار رمزنگاری می‌کند.

#### ۵. `start_packet_capture(self)`

- **شرح**: متدی برای ضبط بسته‌های شبکه‌ای.
- **عملکرد**:
  - از کتابخانه `pyshark` برای ضبط ترافیک شبکه استفاده می‌کند.
  - بسته‌های دریافتی را تجزیه و تحلیل کرده و محتوای آن‌ها را در یک فایل لاگ ذخیره می‌کند.

#### ۶. `start(self)`

- **شرح**: متدی برای شروع عملکرد کلاینت.
- **عملکرد**:
  - اتصال به سرور را برقرار کرده و کلیدها را دریافت می‌کند.
  - منوی انتخاب گزینه‌ها را برای کاربر نمایش می‌دهد و بر اساس انتخاب کاربر اقدام می‌کند.

---

### کلاس Backgammon_Game

کلاس `Backgammon_Game` شامل منطق و گرافیک بازی تخته نرد است که پس از اتصال دو کلاینت به سرور ، می توانند با یکدیگر بازی و چت کنند.

---

## عملکرد wireshark در پروژه

در سه کلاس اصلی `routers` ، `server` و `client` یک تابع به نام `start_packet_capture()` وجود دارد که یک نخ مستقل از اجرای عادی برنامه است و با استفاده از کتابخانه `pyshark` تمام داده هایی که از طریق سوکت های این سه کلاس منتقل می شوند را به همراه شماره پورت مبدا و مقصد دریافت و در فایل `wireshark.log` می نویسد.

## پیش نیازها

این پروژه به کتابخانه‌های زیر نیاز دارد:

- `socket`
- `random`
- `pyshark`
- `asyncio`
- `threading`
- `cryptography`

## نحوه نصب

برای نصب کتابخانه‌های مورد نیاز، از pip استفاده کنید:

```bash
pip install pyshark cryptography
```
