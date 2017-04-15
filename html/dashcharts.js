$(document).ready(function () {

    var donutCharts = {}
    var perhourCharts = {}

    function CreateChartInstance(type,name) {
        if (type == "donut") {
            donutCharts[name] = c3.generate({
                bindto: '#donut' + name,
                data: {
                    columns: [],
                    type: 'donut'
                },
                color: {
                    pattern: ['#4B4A67', '#7E8987', '#8DB580', '#C2CFB2', '#DDD1C7']
                },
                donut: {
                    label: {
                        format: function (value, ratio, id) {
                            return (value);
                        }
                    },
                    title: name.replace(/(^|\s)[a-z]/g,function(f){return f.toUpperCase();})
                }
            });
            donutCharts[name].legend.hide();
        }
        else if (type == "perhour") {
            perhourCharts[name] = c3.generate({
            bindto: '#perhour' + name,
                data: {
                x: 'date',
                columns = []
                //columns: [
                //    ['date', '2014-01-01', '2014-01-10', '2014-01-20', '2014-01-30', '2014-02-01'],
                //    ['sample', 30, 200, 100, 400, 150, 250]
                //]
                },
                axis: {
                    x: {
                        type: 'timeseries'
                    }
                },
                //regions: [
                //    {start: '2014-01-05', end: '2014-01-10'},
                //    {start: new Date('2014/01/15'), end: new Date('20 Jan 2014')},
                //    {start: 1390575600000, end: 1391007600000} // start => 2014-01-25 00:00:00, end => 2014-01-30 00:00:00
                //]
            });
        }
    }


    function setHeaderDataTable(xhr) {
        xhr.setRequestHeader('x-api-key', 'ntdcCpn3lE52HrYX891cnakn3ehqJLYb44ucJ7up');
        //xhr.setRequestHeader('authorization', token);
        }


    function renderDonut(type, name, rspdata) {
        if (type == "donut") {
            CreateChartInstance(type,name)
            var dataArr = {};
            var arr = [];
            rspdata.forEach(function (e) {
                arr.push(e.name);
                dataArr[e.name] = e.estimatedcharges;
            })
            donutCharts[name].load({
                json: [dataArr],
                keys: {
                    value: arr,
                }
            });
        }
        else if (type == "perhour") {
            perhourCharts[name].load({
                columns: [rspdata],
            });
        }
    }

    function requestChartData() {
        return $.ajax({
            url: "https://enq9fomv02.execute-api.us-east-1.amazonaws.com/api/clubchart/" + $("#clubid").val() + "/",
            cache: false,
            type: "GET",
            beforeSend: setHeaderDataTable,
            contentType: 'application/json; charset=utf-8',
        })
        .done(function (data) {
            //console.log(data);
            document.getElementById('currentmonthCount').innerHTML = data.summary[0].current;
            document.getElementById('lastmonthCount').innerHTML = data.summary[0].last;

            var barChart = c3.generate({
                bindto: '#barchart',
                data: {
                    json: data.bymonth,
                    keys: {
                        x: 'monthyear', // it's possible to specify 'x' when category axis
                        value: **PAYERS**,
                    },
                    type: 'bar',
                    groups: [
                        **PAYERS**
                    ],
                    order: 'null'
                },
                //color: {
                //    pattern: ['#203ABB', '#F8AA33']
                //},
                axis: {
                    x: {
                        type: 'category',
                        tick: {
                            rotate: -30,
                            multiline: false
                        },
                        height: 50
                    }
                }
            });

            renderDonut("services", data.byservices);
            renderDonut("tags", data.bytags);
            renderDonut("payers", data.bypayers);
            renderDonut("linked", data.bylinked);

        });
    };

    requestChartData();
});