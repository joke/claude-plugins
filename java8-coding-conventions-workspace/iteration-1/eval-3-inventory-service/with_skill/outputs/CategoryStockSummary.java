public class CategoryStockSummary {

    private final String category;
    private final int totalQuantity;
    private final long productCount;

    public CategoryStockSummary(final String category,
                                final int totalQuantity,
                                final long productCount) {
        this.category = category;
        this.totalQuantity = totalQuantity;
        this.productCount = productCount;
    }

    public String getCategory() {
        return category;
    }

    public int getTotalQuantity() {
        return totalQuantity;
    }

    public long getProductCount() {
        return productCount;
    }
}
