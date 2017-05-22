/**
 * Created by D-N on 07-May-17.
 */

travel.controller('bestOffersCtrl', function($scope, $http) {
    $scope.sort_type = 'price_raw';
    $scope.sort_reverse = false;

    $scope.sort = function(name) {
        if ($scope.sort_type === name) {
            $scope.sort_reverse = !$scope.sort_reverse;
        } else {
            $scope.sort_type = name;
            $scope.sort_reverse = false;
        }
    };

    $scope.flight_popup = function (guid) {
        $scope.flights_loading = true;

        var url = $('#flights-open').attr('data-url').replace('42069', guid);
        $('#flightModal').modal();

        $http.get(url)
            .then(function (response) {
                $scope.flights_loading = false;
                if (response.data.type === 'success') {
                    $scope.flights = response.data.flights;
                }
            }, function (response) {
                $scope.flights_loading = false;
            });
    };

    $http.get($('.main-table').attr('data-url'))
        .then(function (response) {
            if (response.data.type === 'success') {
                $scope.records = response.data.records;
                $scope.done = true;
            }
        });
});