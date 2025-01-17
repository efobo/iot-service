# HOW TO

Команда для запуска
<br>

```
python data-simulator.py --devices 100 --frequency 1 --endpoint http://localhost:50051/data
```

<br>
<ul>
	<li><code>--devices</code>: Указывает количество симулируемых устройств (например, 100).</li>
	<li><code>--frequency</code>: Указывает частоту сообщений от каждого устройства (в сообщениях в секунду). Например, 1.0 означает, что каждое устройство отправляет одно сообщение в секунду.</li>
	<li><code>--endpoint</code>: URL эндпоинта IoT Controller (например, http://localhost:50051/data).</li>
</ul>
