import java.util.List;

public interface ProductRepository {

    List<Product> findAll();

    List<Product> findByCategory(String category);
}
