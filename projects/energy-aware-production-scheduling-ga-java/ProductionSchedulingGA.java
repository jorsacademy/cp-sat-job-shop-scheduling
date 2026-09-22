import java.util.*;
import java.util.stream.Collectors;

class Task {
    final String id;
    final List<TaskMode> modes = new ArrayList<>();
    final List<String> dependencies = new ArrayList<>();

    Task(String id) {
        this.id = Objects.requireNonNull(id);
    }

    Task addMode(TaskMode mode) {
        modes.add(Objects.requireNonNull(mode));
        return this;
    }

    Task addDependency(String taskId) {
        dependencies.add(Objects.requireNonNull(taskId));
        return this;
    }
}

class TaskMode {
    final String id;
    final int duration;
    final double powerConsumption;
    final String requiredMachine;

    TaskMode(String id, int duration, double powerConsumption, String requiredMachine) {
        if (duration <= 0 || powerConsumption < 0) {
            throw new IllegalArgumentException("Duration must be positive and power must be non-negative.");
        }
        this.id = Objects.requireNonNull(id);
        this.duration = duration;
        this.powerConsumption = powerConsumption;
        this.requiredMachine = Objects.requireNonNull(requiredMachine);
    }
}

class Machine {
    final String id;
    final String cellId;

    Machine(String id, String cellId) {
        this.id = Objects.requireNonNull(id);
        this.cellId = Objects.requireNonNull(cellId);
    }
}

class EnergySource {
    final String id;
    final double[] priceProfile;
    final double[] availabilityProfile;

    EnergySource(String id, double[] priceProfile, double[] availabilityProfile) {
        this.id = Objects.requireNonNull(id);
        this.priceProfile = Objects.requireNonNull(priceProfile).clone();
        this.availabilityProfile = Objects.requireNonNull(availabilityProfile).clone();
        if (priceProfile.length != availabilityProfile.length) {
            throw new IllegalArgumentException("Price and availability profiles must have the same length.");
        }
    }
}

class ProductionSystem {
    final List<Task> tasks = new ArrayList<>();
    final List<Machine> machines = new ArrayList<>();
    final List<EnergySource> energySources = new ArrayList<>();
    final int timeHorizon;

    ProductionSystem(int timeHorizon) {
        if (timeHorizon <= 0) throw new IllegalArgumentException("Time horizon must be positive.");
        this.timeHorizon = timeHorizon;
    }

    int machineIndex(String machineId) {
        for (int i = 0; i < machines.size(); i++) {
            if (machines.get(i).id.equals(machineId)) return i;
        }
        return -1;
    }

    int taskIndex(String taskId) {
        for (int i = 0; i < tasks.size(); i++) {
            if (tasks.get(i).id.equals(taskId)) return i;
        }
        return -1;
    }

    void validate() {
        if (tasks.isEmpty()) throw new IllegalStateException("At least one task is required.");
        if (machines.isEmpty()) throw new IllegalStateException("At least one machine is required.");

        Set<String> taskIds = new HashSet<>();
        for (Task task : tasks) {
            if (!taskIds.add(task.id)) throw new IllegalStateException("Duplicate task id: " + task.id);
            if (task.modes.isEmpty()) throw new IllegalStateException("Task has no modes: " + task.id);
            for (TaskMode mode : task.modes) {
                if (machineIndex(mode.requiredMachine) < 0) {
                    throw new IllegalStateException("Unknown machine " + mode.requiredMachine + " for task " + task.id);
                }
            }
        }
        for (Task task : tasks) {
            for (String dependency : task.dependencies) {
                if (taskIndex(dependency) < 0) {
                    throw new IllegalStateException("Unknown dependency " + dependency + " for task " + task.id);
                }
            }
        }
        randomTopologicalOrder(new Random(0));
    }

    int[] randomTopologicalOrder(Random random) {
        int n = tasks.size();
        int[] indegree = new int[n];
        List<List<Integer>> outgoing = new ArrayList<>();
        for (int i = 0; i < n; i++) outgoing.add(new ArrayList<>());

        for (int i = 0; i < n; i++) {
            for (String depId : tasks.get(i).dependencies) {
                int dep = taskIndex(depId);
                if (dep < 0) throw new IllegalStateException("Unknown dependency: " + depId);
                indegree[i]++;
                outgoing.get(dep).add(i);
            }
        }

        List<Integer> available = new ArrayList<>();
        for (int i = 0; i < n; i++) if (indegree[i] == 0) available.add(i);

        int[] order = new int[n];
        int pos = 0;
        while (!available.isEmpty()) {
            int selectedPos = random.nextInt(available.size());
            int task = available.remove(selectedPos);
            order[pos++] = task;
            for (int next : outgoing.get(task)) {
                if (--indegree[next] == 0) available.add(next);
            }
        }

        if (pos != n) throw new IllegalStateException("Task dependencies contain a cycle.");
        return order;
    }
}

class ProductionSchedule {
    int[] taskOrder;
    int[] taskModes;
    int[] machineAssign;
    int[] pauseBefore;

    ProductionSchedule(ProductionSystem system, Random random) {
        int n = system.tasks.size();
        taskOrder = system.randomTopologicalOrder(random);
        taskModes = new int[n];
        machineAssign = new int[n];
        pauseBefore = new int[n];

        for (int taskIndex = 0; taskIndex < n; taskIndex++) {
            Task task = system.tasks.get(taskIndex);
            taskModes[taskIndex] = random.nextInt(task.modes.size());
            TaskMode mode = task.modes.get(taskModes[taskIndex]);
            machineAssign[taskIndex] = system.machineIndex(mode.requiredMachine);
            pauseBefore[taskIndex] = random.nextInt(10);
        }
    }

    ProductionSchedule(ProductionSchedule other) {
        taskOrder = other.taskOrder.clone();
        taskModes = other.taskModes.clone();
        machineAssign = other.machineAssign.clone();
        pauseBefore = other.pauseBefore.clone();
    }
}

class ScheduleFitness {
    final double makespan;
    final double energyCost;
    final double peakPower;
    final double totalFitness;
    final boolean valid;

    ScheduleFitness(double makespan, double energyCost, double peakPower, double totalFitness, boolean valid) {
        this.makespan = makespan;
        this.energyCost = energyCost;
        this.peakPower = peakPower;
        this.totalFitness = totalFitness;
        this.valid = valid;
    }
}

class ProductionOptimizer {
    private final ProductionSystem system;
    private final int populationSize;
    private final int maxGenerations;
    private final double mutationRate;
    private final Random random;

    private double makespanWeight = 0.4;
    private double energyCostWeight = 0.4;
    private double peakPowerWeight = 0.2;

    ProductionOptimizer(ProductionSystem system, int populationSize, int maxGenerations, double mutationRate) {
        if (populationSize < 2 || maxGenerations < 1 || mutationRate < 0 || mutationRate > 1) {
            throw new IllegalArgumentException("Invalid GA parameters.");
        }
        this.system = Objects.requireNonNull(system);
        this.populationSize = populationSize;
        this.maxGenerations = maxGenerations;
        this.mutationRate = mutationRate;
        this.random = new Random();
        system.validate();
    }

    void setWeights(double makespan, double energyCost, double peakPower) {
        if (makespan < 0 || energyCost < 0 || peakPower < 0) {
            throw new IllegalArgumentException("Weights must be non-negative.");
        }
        double sum = makespan + energyCost + peakPower;
        if (sum <= 0) throw new IllegalArgumentException("At least one weight must be positive.");
        makespanWeight = makespan / sum;
        energyCostWeight = energyCost / sum;
        peakPowerWeight = peakPower / sum;
    }

    ProductionSchedule optimize() {
        List<ProductionSchedule> population = initializePopulation();
        ProductionSchedule bestSolution = null;
        double bestFitness = Double.MAX_VALUE;

        for (int generation = 0; generation < maxGenerations; generation++) {
            Map<ProductionSchedule, ScheduleFitness> fitnessMap = new IdentityHashMap<>();
            for (ProductionSchedule schedule : population) {
                ScheduleFitness fitness = evaluateFitness(schedule);
                fitnessMap.put(schedule, fitness);
                if (fitness.totalFitness < bestFitness) {
                    bestFitness = fitness.totalFitness;
                    bestSolution = new ProductionSchedule(schedule);
                }
            }

            if (generation % 10 == 0 || generation == maxGenerations - 1) {
                System.out.printf("Generation %d: Best normalized fitness = %.6f%n", generation, bestFitness);
            }
            population = evolvePopulation(population, fitnessMap);
        }
        return bestSolution;
    }

    ScheduleFitness evaluateFitness(ProductionSchedule schedule) {
        int n = system.tasks.size();
        int[] machineEndTimes = new int[system.machines.size()];
        int[] taskEndTimes = new int[n];
        boolean[] completed = new boolean[n];
        double[] powerProfile = new double[system.timeHorizon];
        boolean valid = true;

        for (int orderPos = 0; orderPos < schedule.taskOrder.length; orderPos++) {
            int taskIndex = schedule.taskOrder[orderPos];
            if (taskIndex < 0 || taskIndex >= n || completed[taskIndex]) {
                valid = false;
                continue;
            }

            Task task = system.tasks.get(taskIndex);
            int modeIndex = schedule.taskModes[taskIndex];
            if (modeIndex < 0 || modeIndex >= task.modes.size()) {
                valid = false;
                continue;
            }
            TaskMode mode = task.modes.get(modeIndex);

            int requiredMachineIndex = system.machineIndex(mode.requiredMachine);
            int assignedMachineIndex = schedule.machineAssign[taskIndex];
            if (assignedMachineIndex != requiredMachineIndex || assignedMachineIndex < 0) {
                valid = false;
                continue;
            }

            int dependencyReadyTime = 0;
            boolean dependenciesReady = true;
            for (String dependencyId : task.dependencies) {
                int dependencyIndex = system.taskIndex(dependencyId);
                if (dependencyIndex < 0 || !completed[dependencyIndex]) {
                    dependenciesReady = false;
                    break;
                }
                dependencyReadyTime = Math.max(dependencyReadyTime, taskEndTimes[dependencyIndex]);
            }
            if (!dependenciesReady) {
                valid = false;
                continue;
            }

            int startTime = Math.max(machineEndTimes[assignedMachineIndex], dependencyReadyTime)
                    + schedule.pauseBefore[taskIndex];
            int endTime = startTime + mode.duration;
            if (startTime < 0 || endTime > system.timeHorizon) {
                valid = false;
                continue;
            }

            for (int t = startTime; t < endTime; t++) {
                powerProfile[t] += mode.powerConsumption;
            }
            machineEndTimes[assignedMachineIndex] = endTime;
            taskEndTimes[taskIndex] = endTime;
            completed[taskIndex] = true;
        }

        for (boolean done : completed) valid &= done;

        double makespan = Arrays.stream(taskEndTimes).max().orElse(0);
        double peakPower = Arrays.stream(powerProfile).max().orElse(0.0);
        double energyCost = calculateEnergyCost(powerProfile);
        double totalFitness = valid ? normalizedWeightedFitness(makespan, energyCost, peakPower) : Double.MAX_VALUE;
        return new ScheduleFitness(makespan, energyCost, peakPower, totalFitness, valid);
    }

    private double calculateEnergyCost(double[] powerProfile) {
        double total = 0.0;
        for (int t = 0; t < powerProfile.length; t++) {
            double remaining = powerProfile[t];
            if (remaining <= 0) continue;

            final int time = t;
            List<EnergySource> sources = system.energySources.stream()
                    .filter(s -> time < s.priceProfile.length && time < s.availabilityProfile.length)
                    .sorted(Comparator.comparingDouble(s -> s.priceProfile[time]))
                    .collect(Collectors.toList());

            for (EnergySource source : sources) {
                double available = Math.max(0.0, source.availabilityProfile[t]);
                double supplied = Math.min(remaining, available);
                total += supplied * source.priceProfile[t];
                remaining -= supplied;
                if (remaining <= 1e-12) break;
            }

            if (remaining > 1e-12) total += remaining * 1_000.0;
        }
        return total;
    }

    private double normalizedWeightedFitness(double makespan, double energyCost, double peakPower) {
        double makespanNorm = makespan / Math.max(1.0, system.timeHorizon);

        double maxPrice = system.energySources.stream()
                .flatMapToDouble(s -> Arrays.stream(s.priceProfile))
                .max().orElse(1.0);
        if (maxPrice <= 0) maxPrice = 1.0;

        double maxTaskPower = system.tasks.stream()
                .flatMap(t -> t.modes.stream())
                .mapToDouble(m -> m.powerConsumption)
                .max().orElse(1.0);
        double maxConcurrentPower = Math.max(1.0, maxTaskPower * system.machines.size());
        double energyScale = Math.max(1.0, maxConcurrentPower * maxPrice * system.timeHorizon);

        double energyNorm = energyCost / energyScale;
        double peakNorm = peakPower / maxConcurrentPower;
        return makespanWeight * makespanNorm
                + energyCostWeight * energyNorm
                + peakPowerWeight * peakNorm;
    }

    private List<ProductionSchedule> initializePopulation() {
        List<ProductionSchedule> population = new ArrayList<>();
        for (int i = 0; i < populationSize; i++) population.add(new ProductionSchedule(system, random));
        return population;
    }

    private List<ProductionSchedule> evolvePopulation(List<ProductionSchedule> population,
                                                       Map<ProductionSchedule, ScheduleFitness> fitnessMap) {
        List<ProductionSchedule> sorted = population.stream()
                .sorted(Comparator.comparingDouble(s -> fitnessMap.get(s).totalFitness))
                .collect(Collectors.toList());

        List<ProductionSchedule> next = new ArrayList<>();
        int eliteCount = Math.max(1, populationSize / 10);
        for (int i = 0; i < eliteCount; i++) next.add(new ProductionSchedule(sorted.get(i)));

        while (next.size() < populationSize) {
            ProductionSchedule offspring = new ProductionSchedule(tournamentSelection(population, fitnessMap));
            mutate(offspring);
            next.add(offspring);
        }
        return next;
    }

    private ProductionSchedule tournamentSelection(List<ProductionSchedule> population,
                                                     Map<ProductionSchedule, ScheduleFitness> fitnessMap) {
        ProductionSchedule best = null;
        double bestFitness = Double.MAX_VALUE;
        for (int i = 0; i < 3; i++) {
            ProductionSchedule candidate = population.get(random.nextInt(population.size()));
            double fitness = fitnessMap.get(candidate).totalFitness;
            if (fitness < bestFitness) {
                bestFitness = fitness;
                best = candidate;
            }
        }
        return Objects.requireNonNull(best);
    }

    private void mutate(ProductionSchedule schedule) {
        if (random.nextDouble() >= mutationRate) return;

        switch (random.nextInt(4)) {
            case 0:
                schedule.taskOrder = system.randomTopologicalOrder(random);
                break;
            case 1:
                mutateModeAndMachine(schedule);
                break;
            case 2:
                mutateMachineAssignment(schedule);
                break;
            case 3:
                int task = random.nextInt(schedule.pauseBefore.length);
                schedule.pauseBefore[task] = Math.max(0,
                        schedule.pauseBefore[task] + random.nextInt(5) - 2);
                break;
            default:
                throw new IllegalStateException("Unexpected mutation type");
        }
    }

    private void mutateModeAndMachine(ProductionSchedule schedule) {
        int taskIndex = random.nextInt(system.tasks.size());
        Task task = system.tasks.get(taskIndex);
        schedule.taskModes[taskIndex] = random.nextInt(task.modes.size());
        TaskMode mode = task.modes.get(schedule.taskModes[taskIndex]);
        schedule.machineAssign[taskIndex] = system.machineIndex(mode.requiredMachine);
    }

    private void mutateMachineAssignment(ProductionSchedule schedule) {
        int taskIndex = random.nextInt(system.tasks.size());
        TaskMode mode = system.tasks.get(taskIndex).modes.get(schedule.taskModes[taskIndex]);
        schedule.machineAssign[taskIndex] = system.machineIndex(mode.requiredMachine);
    }
}

public class ProductionSchedulingGA {
    public static void main(String[] args) {
        System.out.println("=== Energy-Aware Production Scheduling with a Genetic Algorithm ===\n");

        ProductionSystem system = createSampleSystem();
        ProductionOptimizer optimizer = new ProductionOptimizer(system, 100, 200, 0.20);

        System.out.printf("Tasks: %d | Machines: %d | Energy sources: %d | Horizon: %d%n%n",
                system.tasks.size(), system.machines.size(), system.energySources.size(), system.timeHorizon);

        demonstrateOptimization(optimizer, "Balanced", 0.4, 0.4, 0.2);
        demonstrateOptimization(optimizer, "Makespan-focused", 0.8, 0.1, 0.1);
        demonstrateOptimization(optimizer, "Energy-focused", 0.1, 0.8, 0.1);
    }

    private static void demonstrateOptimization(ProductionOptimizer optimizer, String name,
                                                 double makespanWeight, double energyWeight, double peakWeight) {
        System.out.println("=== " + name + " Optimization ===");
        optimizer.setWeights(makespanWeight, energyWeight, peakWeight);

        long started = System.currentTimeMillis();
        ProductionSchedule best = optimizer.optimize();
        long elapsed = System.currentTimeMillis() - started;
        ScheduleFitness fitness = optimizer.evaluateFitness(best);

        System.out.printf("Makespan: %.2f%n", fitness.makespan);
        System.out.printf("Energy cost: %.4f%n", fitness.energyCost);
        System.out.printf("Peak power: %.2f%n", fitness.peakPower);
        System.out.printf("Normalized fitness: %.6f%n", fitness.totalFitness);
        System.out.printf("Runtime: %d ms%n", elapsed);
        System.out.println("Task order: " + Arrays.toString(best.taskOrder));
        System.out.println("Task modes: " + Arrays.toString(best.taskModes));
        System.out.println("Machine assignments: " + Arrays.toString(best.machineAssign));
        System.out.println("Pause-before times: " + Arrays.toString(best.pauseBefore));
        System.out.println();
    }

    private static ProductionSystem createSampleSystem() {
        ProductionSystem system = new ProductionSystem(100);

        system.machines.add(new Machine("M1", "Cell1"));
        system.machines.add(new Machine("M2", "Cell1"));
        system.machines.add(new Machine("M3", "Cell2"));

        Task load = new Task("LoadPart")
                .addMode(new TaskMode("Manual", 5, 2.0, "M1"))
                .addMode(new TaskMode("Auto", 3, 4.0, "M1"));

        Task fix = new Task("FixPart")
                .addMode(new TaskMode("Standard", 4, 3.0, "M1"))
                .addMode(new TaskMode("Fast", 2, 6.0, "M1"))
                .addDependency("LoadPart");

        Task rotate = new Task("Rotate")
                .addMode(new TaskMode("Slow", 8, 5.0, "M2"))
                .addMode(new TaskMode("Fast", 4, 10.0, "M2"))
                .addDependency("FixPart");

        Task process = new Task("Process")
                .addMode(new TaskMode("LowPower", 15, 8.0, "M3"))
                .addMode(new TaskMode("HighPower", 10, 15.0, "M3"))
                .addDependency("Rotate");

        Task unload = new Task("Unload")
                .addMode(new TaskMode("Manual", 6, 1.0, "M2"))
                .addMode(new TaskMode("Auto", 4, 3.0, "M2"))
                .addDependency("Process");

        system.tasks.addAll(Arrays.asList(load, fix, rotate, process, unload));

        double[] gridPrices = new double[100];
        double[] gridAvailability = new double[100];
        Arrays.fill(gridPrices, 0.15);
        Arrays.fill(gridAvailability, 1000.0);
        for (int t = 17; t < 22; t++) gridPrices[t] = 0.30;

        double[] solarPrices = new double[100];
        double[] solarAvailability = new double[100];
        Arrays.fill(solarPrices, 0.0);
        for (int i = 0; i < 100; i++) {
            double hour = i % 24;
            if (hour >= 6 && hour <= 18) {
                solarAvailability[i] = 12.0 * Math.sin(Math.PI * (hour - 6.0) / 12.0);
            }
        }

        system.energySources.add(new EnergySource("Solar", solarPrices, solarAvailability));
        system.energySources.add(new EnergySource("Grid", gridPrices, gridAvailability));
        return system;
    }
}
