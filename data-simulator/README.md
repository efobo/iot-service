# HOW TO

Команда для запуска
<br>
```
python3 data-simulator.py --devices 100 --frequency 1 --endpoint http://<iot-controller-host>:50051/data
```
<br>

```
python data-simulator.py --devices 100 --frequency 1 --endpoint http://localhost:50051/data
```

<br>
<ul>
	<li>`--devices`: Указывает количество симулируемых устройств (например, 100).</li>
	<li>`--frequency`: Указывает частоту сообщений от каждого устройства (в сообщениях в секунду). Например, 1.0 означает, что каждое устройство отправляет одно сообщение в секунду.</li>
	<li>`--endpoint`: URL эндпоинта IoT Controller (например, http://localhost:50051/data).</li>
</ul>
