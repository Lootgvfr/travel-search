/**
 * Created by D-N on 07-May-17.
 */

travel.controller('adminCtrl', function($scope, $http) {
    $scope.stats_request = function() {
        if (!$('#year').val()){
            $scope.error_text = 'Введіть бажаний рік'
        }
        else if (!$scope.loading) {
            $scope.loading = true;
            $scope.error_text = '';
            $scope.stats_img = '';
            $scope.pred_img = '';
            var url = $('#stats-btn').attr('data-url').replace(228, $('#year').val());

            $http.get(url)
                .then(function (response) {
                    if (response.data.type === 'success') {
                        $scope.stats_img = response.data.statistics_url;
                    }
                    else {
                        $scope.error_text = response.data.message;
                    }
                    $scope.loading = false;
                }, function (response) {
                    $scope.loading = false;
                });
        }
    };

    $scope.pred_request = function() {
        if (!$('#year').val()) {
            $scope.error_text = 'Введіть бажаний рік'
        }
        else if (!$scope.loading) {
            $scope.loading = true;
            $scope.error_text = '';
            $scope.stats_img = '';
            $scope.pred_img = '';
            var url = $('#pred-btn').attr('data-url').replace(228, $('#year').val());

            $http.get(url)
                .then(function (response) {
                    if (response.data.type === 'success') {
                        $scope.stats_img = response.data.statistics_url;
                        $scope.pred_img = response.data.prediction_url;
                    }
                    else {
                        $scope.error_text = response.data.message;
                    }
                    $scope.loading = false;
                }, function (response) {
                    $scope.loading = false;
                });
        }
    };
});