/**
 * Created by D-N on 07-May-17.
 */

travel.controller('searchResultsCtrl', function($scope, $http) {
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

    $http.get($('.main-table').attr('data-url'))
        .then(function (response) {
            if (response.data.type === 'success') {
                $scope.records = response.data.records;
                $scope.done = true;
            }
        });
});


