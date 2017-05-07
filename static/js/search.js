/**
 * Created by D-N on 07-May-17.
 */

travel.controller('searchResultsCtrl', function($scope, $http) {
    $http.get($('.header-row').attr('data-url'))
        .then(function (response) {
            if (response.data.type === 'success') {
                $scope.records = response.data.records;
            }
        });
});
