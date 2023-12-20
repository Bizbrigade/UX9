$(document).ready(function () {
    //-------------------------------SELECT CASCADING-------------------------//
    var selectedCountry = (selectedRegion = selectedCity = countryCode = "");

    // This is a demo API key for testing purposes. You should rather request your API key (free) from http://battuta.medunes.net/
    var BATTUTA_KEY = "00000000000000000000000000000000";
    // Populate country select box from battuta API
    url =
        "https://battuta.medunes.net/api/country/all/?key=" +
        BATTUTA_KEY +
        "&callback=?";

    // EXTRACT JSON DATA.
    $.getJSON(url, function (data) {
        console.log(data);
        $.each(data, function (index, value) {
            // APPEND OR INSERT DATA TO SELECT ELEMENT. Set the country code in the id section rather than in the value.
            $("#country").append(
                '<option id="' +
                value.code +
                '" value="' +
                value.name +
                '">' +
                value.name +
                "</option>"
            );
        });
    });
    // Country selected --> update region list .
    $("#country").change(function () {
        selectedCountry = this.options[this.selectedIndex].text;
        // get the id of the option which has the country code.
        countryCode = $(this)
            .children(":selected")
            .attr("id");
        // Populate country select box from battuta API
        url =
            "https://battuta.medunes.net/api/region/" +
            countryCode +
            "/all/?key=" +
            BATTUTA_KEY +
            "&callback=?";
        $.getJSON(url, function (data) {
            $("#region option").remove();
            $('#region').append('<option value="">Please select your region</option>');
            $.each(data, function (index, value) {
                // APPEND OR INSERT DATA TO SELECT ELEMENT.
                $("#region").append(
                    '<option value="' + value.region + '">' + value.region + "</option>"
                );
            });
        });
    });
    // Region selected --> updated city list
    $("#region").on("change", function () {
        selectedRegion = this.options[this.selectedIndex].text;
        // Populate country select box from battuta API
        // countryCode = $("#country").val();
        region = $("#region").val();
        url =
            "https://battuta.medunes.net/api/city/" +
            countryCode +
            "/search/?region=" +
            region +
            "&key=" +
            BATTUTA_KEY +
            "&callback=?";
        $.getJSON(url, function (data) {
            console.log(data);
            $("#city option").remove();
            $('#city').append('<option value="">Please select your city</option>');
            $.each(data, function (index, value) {
                // APPEND OR INSERT DATA TO SELECT ELEMENT.
                $("#city").append(
                    '<option value="' + value.city + '">' + value.city + "</option>"
                );
            });
        });
    });
    // city selected --> update location string
    $("#city").on("change", function () {
        selectedCity = this.options[this.selectedIndex].text;
        $("#location").html(
            "Locatation: Country: " +
            selectedCountry +
            ", Region: " +
            selectedRegion +
            ", City: " +
            selectedCity
        );
    });
});

// very simple process form function to collect input values.
function processForm() {
    var username = (password = country = region = city = "");
    username = $("#username").val();
    password = $("#password").val();
    country = $("#country").val();
    region = $("#region").val();
    city = $("#city").val();
    if (
        // username != "" &&
        // password != "" &&
        country != "" &&
        region != "" &&
        city != ""
    ) {
        $("#location").html(
            // "Username: " +
            //   username +
            //   " /Password: " +
            //   password +
            "Locatation: Country: " +
            country +
            ", Region: " +
            region +
            ", City: " +
            city
        );
    } else {
        $("#location").html("Fill Country, Region and City to view the location");
        return false;
    }
}