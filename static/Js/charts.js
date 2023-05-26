//Chart1 Javascript
import { histData , piechartData, trees, crops, builtArea } from "./chartdata.js";

const piechartArray = []
for (var i = 0 ; i < 11 ; i++)
{
  piechartArray.push(piechartData[i]);
}


// Bar chart
const ctx = document.getElementById('myChart');
        new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['2019', '2020', '2021', '2022', '2023'],
            datasets: [{
              label: 'Trees',
              backgroundColor: 'fillPattern',
              borderColor: 'rgb(155,99,132)',
              data: trees,
              borderWidth: 1
            }]
          },
          options: {
            aspectRatio: 1.8,
            scales: {
              y: {
                beginAtZero: true
              }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Trees'
                  }
            }
          }
        });


// PieChart
const cty = document.getElementById('chart2');
        new Chart(cty, {
          type: 'pie',
          data: {
            labels: ['Unmarked', 'Water', 'Trees', 'Grass', 'Flooded vegetation', 'Crops', 'Scrub', 'Built area', 'Bare', 'Snow', 'Cloud'],
            datasets: [{
              // label: 'Landcover Percentage',
              backgroundColor: ['#9E4784', '#CD5888', '#FCC8D1', '#D27685', '#CB1C8D', '#7F167F'],
              borderColor: 'rgb(255, 255, 255)',
              data: piechartArray,
              borderWidth: 1
            }]
          },
          options: {
            aspectRatio: 1.8,
            scales: {
              y: {
                beginAtZero: true
              }
            }
          }
        });

// Line chart
const ctz = document.getElementById('chart3');
    new Chart(ctz, {
        type: 'line',
        data: {
          labels: ['2018', '2019', '2020', '2021', '2022'],
          datasets: [{
            label: 'trees',
            backgroundColor: 'rgb(0, 0, 0)',
            borderColor: '#863A6F',
            data: trees,
          },{
            label: 'Crops',
            backgroundColor: 'rgb(0, 0, 0)',
            borderColor: '#CB1C8D',
            borderColor: '#CB1C8D',
            data: crops,
          },{
            label: 'Build Area',
            backgroundColor: 'rgb(0, 0, 0)',
            borderColor: '#CB1C8D',
            data: builtArea,
          },]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });