using Newtonsoft.Json;
using RWParcerCore.Domain.DTOs;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;
using System.Diagnostics;
using System.Text.Json;
using System.Web;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class RWParcer(HttpClient httpClient) : IRWRepository
    {
        private readonly HttpClient _httpClient = httpClient;
        private readonly string GetStationsUrl = "https://pass.rw.by/ru/ajax/autocomplete/search/?term=";
        private readonly string GetTrainsBaseUrl = "https://apicast.rw.by/v1/rasp/ru/index/route";
        private readonly string GetSeatsBaseUrl = "https://pass.rw.by/ru/ajax/route/car_places";

        public async Task<List<RepoStation>> GetStationsAsync(string pref)
        {
            string fullUrl = GetStationsUrl + pref;
            HttpResponseMessage response = await _httpClient.GetAsync(fullUrl);

            if (!response.IsSuccessStatusCode)
            {
                Console.WriteLine($"Ошибка: {response.StatusCode}");
                return [];
            }

            string json = await response.Content.ReadAsStringAsync();
            List<RepoStation>? stations = JsonConvert.DeserializeObject<List<RepoStation>>(json);
            return stations ?? [];
        }

        public async Task<List<RepoTrain>> GetTrainsAsync(RouteVO route)
        {
            var builder = new UriBuilder(GetTrainsBaseUrl);

            var query = HttpUtility.ParseQueryString(builder.Query);
            query["format"] = "json";
            query["from_exp"] = route.From.Exp;
            query["to_exp"] = route.To.Exp;
            query["date"] = "everyday";
            query["user_key"] = "c2a3d81674b7f4c9e4af16bdba110d53";
            builder.Query = query.ToString();

            HttpResponseMessage response = await _httpClient.GetAsync(builder.ToString());

            if (!response.IsSuccessStatusCode)
            {
                Console.WriteLine($"Ошибка: {response.StatusCode}");
                return [];
            }

            string json = await response.Content.ReadAsStringAsync();
            using JsonDocument doc = JsonDocument.Parse(json);
            JsonElement root = doc.RootElement;

            if (!root.TryGetProperty("routes", out JsonElement routesElement))
            {
                Console.WriteLine("Ошибка: JSON не содержит маршрутов.");
                return [];
            }

            string routesJson = routesElement.GetRawText();
            var settings = new JsonSerializerSettings
            {
                Error = (sender, args) =>
                {
                    Console.WriteLine($"Ошибка при десериализации {args.ErrorContext.Path}: {args.ErrorContext.Error.Message}");
                    args.ErrorContext.Handled = true;
                }
            };

            List<RepoTrain>? trains = JsonConvert.DeserializeObject<List<RepoTrain>>(routesJson, settings);
            return trains ?? [];
        }

        public async Task<Dictionary<int, List<int>>> GetSeatsAsync(SubscriptionVO subscription)
        {
            Dictionary<int, List<int>> result = [];

            UriBuilder builder = new(GetSeatsBaseUrl);
            for (int carType = 1; carType <= 5; carType++)
            {
                var query = HttpUtility.ParseQueryString(builder.Query);
                query["from"] = subscription.Train.StationFrom.Exp;
                query["to"] = subscription.Train.StationTo.Exp;
                query["date"] = subscription.Date.ToString("yyyy-MM-dd");
                query["train_number"] = subscription.Train.TrainNumber;
                query["car_type"] = carType.ToString();
                builder.Query = query.ToString();

                HttpResponseMessage response = await _httpClient.GetAsync(builder.ToString());

                if (!response.IsSuccessStatusCode)
                {
                    Debug.WriteLine($"Ошибка: {response.StatusCode}");
                    return [];
                }

                string json = await response.Content.ReadAsStringAsync();
                using JsonDocument doc = JsonDocument.Parse(json);
                JsonElement root = doc.RootElement;

                if (root.TryGetProperty("tariffs", out JsonElement tariffsElement))
                {
                    foreach (JsonElement tariff in tariffsElement.EnumerateArray())
                    {
                        if (tariff.TryGetProperty("cars", out JsonElement carsElement))
                        {
                            foreach (JsonElement car in carsElement.EnumerateArray())
                            {
                                if (car.TryGetProperty("number", out JsonElement numberElement) &&
                                    car.TryGetProperty("emptyPlaces", out JsonElement placesElement))
                                {
                                    string? carNumberStr = numberElement.GetString();
                                    if (carNumberStr == null)
                                    {
                                        Debug.WriteLine("carNumberStr null");
                                        continue;
                                    }
                                    int carNumber = int.Parse(carNumberStr);
                                    List<int> emptySeats = [];

                                    foreach (JsonElement seat in placesElement.EnumerateArray())
                                    {
                                        string? seatStr = seat.GetString();
                                        if (seatStr == null)
                                        {
                                            Debug.WriteLine("seatStr null");
                                            continue;
                                        }
                                        emptySeats.Add(int.Parse(seatStr));
                                    }

                                    result[carNumber] = emptySeats;
                                }
                            }
                        }
                    }
                }
            }
            return result;
        }
    }
}
