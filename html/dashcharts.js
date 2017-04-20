$(document).ready(function () {

    var barChart = c3.generate({
        bindto: '#last6monthbarchart',
        data: {
            x : 'x',
        columns: [
            ['x', '03-2017', '02-2017', '01-2017', '12-2016', '11-2016', '10-2016'],
            ['514046899996', 0, 0, 0, 0, 0, 50.78987],
            ['745716881695', 0, 0, 0, 0, 0, 108.27369],
        ],
        type: 'bar'
        });

    });

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

};
