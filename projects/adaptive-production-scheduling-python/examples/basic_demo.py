from adaptive_scheduler import AdaptiveProductionScheduler, Machine, Product
from adaptive_scheduler.reporting import production_dataframe, utilization_dataframe


def main() -> None:
    products = [
        Product(name="Smartphone", margin=300, priority=1),
        Product(name="Tablet", margin=200, priority=2),
        Product(name="Wearable", margin=150, priority=3),
    ]
    machines = [
        Machine("Machine_A", 30, "Smartphone", maintenance_probability=0.05),
        Machine("Machine_B", 20, "Tablet", maintenance_probability=0.05),
        Machine("Machine_C", 25, "Wearable", maintenance_probability=0.05),
    ]
    scheduler = AdaptiveProductionScheduler(
        products, machines, ["Morning", "Afternoon", "Night"], seed=42
    )
    result = scheduler.generate_schedule(
        {"Smartphone": 100, "Tablet": 75, "Wearable": 50}
    )

    print("PRODUCTION PLAN")
    print(production_dataframe(result))
    print("\nMACHINE UTILIZATION (%)")
    print(utilization_dataframe(result))
    print("\nKPIs")
    for key, value in result["kpis"].items():
        print(f"{key}: {value}")

    recommendations = scheduler.generate_recommendations(result)
    if recommendations:
        print("\nRECOMMENDATIONS")
        for item in recommendations:
            print(f"- {item}")


if __name__ == "__main__":
    main()
