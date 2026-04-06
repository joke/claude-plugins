public class ScheduledTask implements Comparable<ScheduledTask> {

    private final String name;
    private final int priority;

    public ScheduledTask(final String name, final int priority) {
        this.name = name;
        this.priority = priority;
    }

    public String getName() {
        return name;
    }

    public int getPriority() {
        return priority;
    }

    @Override
    public int compareTo(final ScheduledTask other) {
        return Integer.compare(other.priority, this.priority);
    }
}
