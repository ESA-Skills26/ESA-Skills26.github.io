# ESA Passport — ربط Google Sheet

الصفحة: `https://esa-skills26.github.io/passport/`
زرار **ESA Passport** في هيدر الموقع، وكارت «خريج ESA؟» في قسم التحقق، الاتنين بيوصّلوا لها.

## 1) الشيت
1. اعمل Google Sheet جديد باسم **ESA Passport**.
2. Extensions → Apps Script، امسح الموجود والصق محتوى `Code.gs`، واحفظ.
3. شغّل الدالة `setup` مرة واحدة (هيطلب صلاحيات — وافق). هيعمل 4 تبويبات:

| التبويب | الأعمدة |
|---|---|
| Graduates | graduate_id, name_ar, name_en, tier, status, joined_date, phone, email, marketing_consent, notes |
| Certificates | certificate_id, graduate_id, program, issue_date, status |
| Offers | active, title_ar, title_en, details_ar, details_en, how_ar, how_en, partner, tier, valid_until |
| Events | active, title_ar, title_en, date, place_ar, place_en, link |

- **tier**: Graduate / Achiever / Ambassador — **status**: active / suspended
- شهادة الخريج تتربط بيه عن طريق نفس `graduate_id` في تبويب Certificates.
- العرض أو الفعالية يظهروا على الموقع لما `active = yes` (والعرض لسه في مدة صلاحيته).

## 2) أرقام الخريجين
من قائمة **ESA Passport** في الشيت → **Generate missing Graduate IDs**:
بيدّي كل خريج ملوش رقم رقمًا عشوائيًا زي `ESA-G26-7KQ4M`، عشان محدش يقدر يخمّن أرقام الخريجين التانيين ويشوف أساميهم.
و **Copy card link for selected row** بيطلعلك رابط البطاقة اللي تبعته للخريج في رسالة التفعيل.

## 3) النشر
Apps Script → Deploy → New deployment → Web app
- Execute as: **Me**
- Who has access: **Anyone**

انسخ الرابط اللي آخره `/exec` وحطه في `passport/config.js`:
```js
API_URL: "https://script.google.com/macros/s/XXXX/exec",
```
أي تعديل في الشيت بيظهر على الموقع فورًا (العروض والفعاليات بعد 5 دقايق بحد أقصى).
لو عدّلت الكود نفسه: Deploy → Manage deployments → Edit → New version (الرابط يفضل زي ما هو).

## الخصوصية
الموقع بيستقبل **بس**: الاسم، المستوى، الحالة، تاريخ الانضمام، وشهادات الخريج — لما حد يكتب رقمه بالظبط.
الموبايل والإيميل والموافقات والملاحظات **عمرها ما بتطلع** من الشيت. الشيت نفسه يفضل خاص (ما تعملهوش Share لـ Anyone).

## تجربة قبل الربط
`/passport/?demo=1` بيعرض بطاقة وعروض تجريبية للمعاينة بس.
