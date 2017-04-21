
var barChart = c3.generate({
        bindto: '#last6month',
        data: {
            x: 'x',
            url: 'estimate_month_to_date_payer.json',
            mimeType: 'json',
            type: 'bar'
        },
    axis: {
        x: {
            type: 'category' // this needed to load string x value
        }
    }
 });


