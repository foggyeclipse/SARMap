function formatDate(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
}

const currentDate = new Date();
const formattedDate = formatDate(currentDate);
document.getElementById('date_of_finding').value = formattedDate;

function parseCoordinate(coord) {
    return parseFloat(coord.replace(',', '.'));
}

const hours = String(currentDate.getHours()).padStart(2, '0');
const minutes = String(currentDate.getMinutes()).padStart(2, '0');
const currentTime = `${hours}:${minutes}`;
document.getElementById('time_of_finding').value = currentTime;

$(document).ready(function () {
    $('#toggleAdditionalFields').click(function () {
        $('#additional_fields').toggleClass('hidden-input');
        if (!$('#additional_fields').hasClass('hidden-input')) {
            $('#myTab .nav-link').first().tab('show');
        }
    });

    $('#tab2 input[type="number"]').on('input', function () {
        var value = parseFloat($(this).val());
        if (value < 0 || value > 1) {
            alert('Коэффициент должен быть в пределах от 0 до 1');
            $(this).val('');
        }
    });

    $('#dataForm').on('submit', function (e) {
        e.preventDefault();
        
        $('#overlay').show();
        $('#loader').show();

        var data = {
            date_of_loss: $('#date_of_loss').val(),
            time_of_loss: $('#time_of_loss').val(),
            date_of_finding: $('#date_of_finding').val(),
            time_of_finding: $('#time_of_finding').val(),
            age: $('#age').val(),
            gender: $('#gender').val(),
            physical_condition: $('#physical_condition').val(),
            mental_condition: $('#mental_condition').val(),
            experience: $('#experience').val() || null,
            local_knowledge: $('#local_knowledge').val() || null,
            phone: $('#phone').val() || null,
            terrain_passability: $('#terrain_passability').val() || null,
            path_curvature: $('#path_curvature').val() || null,
            slope_angle: $('#slope_angle').val() || null,
            coordinates_psr: {
                latitude: parseCoordinate($('#psr_lat').val()),
                longitude: parseCoordinate($('#psr_lon').val())
            },
            coordinates_finding: {
                latitude: parseCoordinate($('#finding_lat').val()),
                longitude: parseCoordinate($('#finding_lon').val())
            }
        };

        $.ajax({
            url: '/radius',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (response) {
                if (response && response.coordinates_psr) {
                    document.getElementById('result').classList.add('alert', 'alert-info');
                    document.getElementById('result').innerHTML = "Вероятности поведения потерявшегося на текущий момент:<br>";
                    document.getElementById('result').innerHTML += response.behavior.replace(/%/g, '%  <br>');
                    $('#loader').hide();
                    $('#overlay').hide();
                } else {
                    $('#overlay').hide();
                    $('#loader').hide();
                    alert('Не удалось получить координаты.');
                }
            },
            error: function (xhr, status, error) {
                console.error('Error:', status, error);
                $('#overlay').hide();
                $('#loader').hide();
                alert('Ошибка при отправке данных.');
            }
        });
    });
});
