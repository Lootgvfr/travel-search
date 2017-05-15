/**
 * Created by D-N on 09/02/2017.
 */


$(document).ajaxStart(function () {
    $('.ajax-btn').each(function () {
        $(this).prop('disabled', true);
    });
}).ajaxStop(function () {
    $('.ajax-btn').each(function () {
        $(this).prop('disabled', false);
    });
});

var travel = angular.module('travel', ['ngAnimate']);
