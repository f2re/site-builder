@orchestrator неправильно фильтруется описание товара - оно попадает с тегами, не выделяется жэирным ссылки, не скачиваются изображения по ссылке (или вставлять их в тап тап со ссылками), надо реализовать полное переформатирование описания товара вот пример: <p><span>Программный модуль (прошивка для адаптера </span><a href="http://mad-auto.ru/index.php?route=product/product&amp;path=64_65&amp;product_id=51" target="_blank">WiFi OBD2</a><span>) WiFi Dashboard представляет собой кроссплаторменную виртуальную панель приборов диагностических параметров электронных блоков управления.</span></p><p><span><br></span></p>

<iframe id="docIframe" src="https://mad-auto.ru/doc_wifi_adapters/virtualnaja_pribornaja_panel/index.html" scrolling="no" frameborder="0" width="100%" style="height: 3480px;"></iframe>

<script>
    window.addEventListener('message', function (e) {
        if (e.data.docIframeHeight !== undefined)
        {
  			// console.log('Message from doc');

            var iframe = document.getElementById('docIframe');

            if (iframe) {
  				// console.log('Set docIframe height: ' + e.data.docIframeHeight);
                iframe.style.height = e.data.docIframeHeight;
                iframe.setAttribute("scrolling", "no");;
            }
        }
    });
</script><p></p><p></p> <p></p>
<p><span style="font-family: Arial; font-size: 18px;">Встречаем! Новая тема панели приборов от Ивана Ярёменко и
        обновлённый интерфейс версии 10.1.1 для адаптера <b><a href="index.php?route=product/category&amp;path=64_65" target="_blank">WiFi OBD2</a>.</b></span></p>
<p><span style="font-family: Arial; font-size: 18px;"><b>Изменения:</b></span></p>
<p><span style="font-family: Arial; font-size: 18px;">- добавлена новая тема панели приборов Sport Round;</span></p>
<p><font face="Arial"><span style="font-size: 18px;">- в темах Sport Flat, Sport Round добавлены возможности:</span></font></p>
<p><font face="Arial"><span style="font-size: 18px;">&nbsp;&nbsp;* отображения мин/макс значений;</span></font></p>
<p><font face="Arial"><span style="font-size: 18px;">&nbsp;&nbsp;* отображения единиц измерений;</span></font></p>
<p><font face="Arial"><span style="font-size: 18px;">&nbsp;&nbsp;* изменения максимального числа оборотов тахометра;</span></font></p>
<p><span style="font-family: Arial; font-size: 18px;">- реализовано выравнивание десятичных чисел на панели приборов;</span></p>
<p><span style="font-family: Arial; font-size: 18px;">- добавлена возможность вывода флагов режимов ЭБУ на панель приборов;</span></p>
<p><span style="font-family: Arial; font-size: 18px;">- настройки панели приборов перенесены в “Локальные настройки”;</span></p>
<p><span style="font-family: Arial; font-size: 18px;">- изменена логика глобальных настроек;</span></p>
<p><span style="font-family: Arial; font-size: 18px;">- добавлен запрет выключения экрана мобильных устройств;</span></p>
<p><span style="font-family: Arial; font-size: 18px;"><br></span></p>
<div><span style="font-family: Arial; font-size: 18px;"><br></span></div>
<img style="width: 100%;" src="https://i.ibb.co/yfhTjrw/sport-Round3.jpg" alt="sport-Round3" border="0">
<div><span style="font-family: Arial; font-size: 18px;"><br></span></div>
<img style="width: 100%;" src="https://i.ibb.co/HKCgF8M/sport-Round1.jpg" alt="sport-Round1" border="0">
<div><span style="font-family: Arial; font-size: 18px;"><br></span></div>
<img style="width: 100%;" src="https://i.ibb.co/Lv71Pgm/sport-Round2.jpg" alt="sport-Round2" border="0">
<div><span style="font-family: Arial; font-size: 18px;"><br></span></div>
<img style="width: 100%;" src="https://i.ibb.co/qYYFfwH/sport-Round6.png" alt="sport-Round6" border="0">
<div><span style="font-family: Arial; font-size: 18px;"><br></span></div>
<img style="width: 100%;" src="https://i.ibb.co/JCPjLz7/sport-Round7.png" alt="sport-Round7" border="0">
<div><span style="font-family: Arial; font-size: 18px;"><br></span></div>
<img style="width: 100%;" src="https://i.ibb.co/3yrr6fz/sport-Round8.png" alt="sport-Round8" border="0">

сам не пиши код, делегируй агентам. в конце запусти тесты и линты перед коммитом, закоммить изменения