import { useEffect, useMemo, useState } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const images = [
  'photo-1496181133206-80ce9b88a853',
  'photo-1505740420928-5e560c06d30e',
  'photo-1587829741301-dc798b83add3',
  'photo-1523275335684-37898b6baf30',
  'photo-1542291026-7eec264c27ff',
  'photo-1526738549149-8e07eca6c147',
]

const money = value => new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
}).format(Number(value))

function App() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('All')
  const [cart, setCart] = useState([])
  const [cartOpen, setCartOpen] = useState(false)
  const [customerName, setCustomerName] = useState('')
  const [customerEmail, setCustomerEmail] = useState('')
  const [checkoutLoading, setCheckoutLoading] = useState(false)
  const [checkoutError, setCheckoutError] = useState('')
  const [orderResult, setOrderResult] = useState(null)


  useEffect(() => {
    fetch(`${API_BASE}/products`)
      .then(response => {
        if (!response.ok) throw new Error('Unable to load products')
        return response.json()
      })
      .then(data => {
        setProducts(data.filter(p => !p.name.toLowerCase().startsWith('pytest product')))
        setError('')
      })
      .catch(() => setError('Could not connect to the product service. Please try again.'))
      .finally(() => setLoading(false))
  }, [])

  const categories = ['All', 'Electronics', 'Accessories']

  const filteredProducts = useMemo(() => {
    return products.filter(product => {
      const name = product.name.toLowerCase()
      const matchesSearch = name.includes(search.toLowerCase())
      const matchesCategory =
        category === 'All' ||
        (category === 'Electronics' && /laptop|phone|tablet|monitor/.test(name)) ||
        (category === 'Accessories' && !/laptop|phone|tablet|monitor/.test(name))
      return matchesSearch && matchesCategory
    })
  }, [products, search, category])

  const addToCart = product => {
    setCart(current => {
      const existing = current.find(item => item.id === product.id)
      if (existing) {
        return current.map(item =>
          item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        )
      }
      return [...current, { ...product, quantity: 1 }]
    })
  }

  const changeQuantity = (id, amount) => {
    setCart(current =>
      current
        .map(item => item.id === id ? { ...item, quantity: item.quantity + amount } : item)
        .filter(item => item.quantity > 0)
    )
  }


  const submitCheckout = async event => {
    event.preventDefault()
    setCheckoutError('')
    setCheckoutLoading(true)
    setOrderResult(null)

    const request = async (url, options = {}) => {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...(options.headers || {}),
        },
      })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(data.detail || `Request failed: ${response.status}`)
      }
      return data
    }

    try {
      const email = customerEmail.trim().toLowerCase()
      let customer

      try {
        customer = await request(`${API_BASE}/users`, {
          method: 'POST',
          body: JSON.stringify({
            name: customerName.trim(),
            email,
          }),
        })
      } catch (error) {
        if (!String(error.message).includes('409') &&
            !String(error.message).toLowerCase().includes('already exists')) {
          throw error
        }

        const users = await request(`${API_BASE}/users`)
        customer = users.find(user =>
          user.email.toLowerCase() === email
        )

        if (!customer) throw error
      }

      const completed = []

      for (const item of cart) {
        const order = await request(`${API_BASE}/orders`, {
          method: 'POST',
          body: JSON.stringify({
            user_id: customer.id,
            product_id: item.id,
            quantity: item.quantity,
          }),
        })

        const payment = await request(`${API_BASE}/payments`, {
          method: 'POST',
          body: JSON.stringify({
            order_id: order.id,
            amount: Number(item.price) * item.quantity,
            method: 'SIMULATED',
          }),
        })

        completed.push({ order, payment, product: item.name })
      }

      setOrderResult(completed)
      setCart([])
    } catch (error) {
      setCheckoutError(error.message || 'Checkout failed. Please try again.')
    } finally {
      setCheckoutLoading(false)
    }
  }

  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0)
  const cartTotal = cart.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0)

  return (
    <div className="store">
      <div className="announcement">
        ✦ Welcome to ShopSphere — discover something great today
      </div>

      <header className="header">
        <a className="brand" href="#">
          <span className="brand-icon">S</span>
          ShopSphere<span className="brand-dot">.</span>
        </a>

        <nav className="nav">
          <a href="#home">Home</a>
          <a href="#products">Shop</a>
          <a href="#about">About</a>
        </nav>

        <div className="header-actions">
          <label className="search-box">
            <span>⌕</span>
            <input
              value={search}
              onChange={event => setSearch(event.target.value)}
              placeholder="Search products..."
            />
          </label>
          <button className="cart-button" onClick={() => setCartOpen(true)}>
            <span>Bag</span>
            <span className="cart-count">{cartCount}</span>
          </button>
        </div>
      </header>

      <main>
        <section className="hero" id="home">
          <div className="hero-content">
            <span className="eyebrow">THE EVERYDAY COLLECTION</span>
            <h1>Good finds.<br /><span>Great living.</span></h1>
            <p>Discover thoughtfully selected essentials for your work, life and everything in between.</p>
            <a className="primary-button" href="#products">Explore collection <span>→</span></a>
            <div className="hero-note">A better way to shop, all in one place.</div>
          </div>
          <div className="hero-visual">
            <div className="hero-circle"></div>
            <img
              src="https://images.unsplash.com/photo-1498049794561-7780e7231661?w=1000&q=85"
              alt="Modern electronics collection"
            />
            <div className="floating-card">
              <span>✦</span>
              <div><strong>Find your next favourite</strong><small>Explore the collection</small></div>
            </div>
          </div>
          <div className="hero-index">01 / 03</div>
        </section>

        <section className="benefits" id="about">
          <div><span>✧</span><strong>Curated products</strong><small>Picked for everyday life</small></div>
          <div><span>◇</span><strong>Simple shopping</strong><small>Easy browsing experience</small></div>
          <div><span>↗</span><strong>Made for you</strong><small>Discover your next favourite</small></div>
        </section>

        <section className="products-section" id="products">
          <div className="section-heading">
            <div>
              <span className="eyebrow">THE SHOP</span>
              <h2>Explore our collection<span>.</span></h2>
              <p>Useful things. Thoughtful choices. Everyday favourites.</p>
            </div>
            <div className="product-count">{products.length} products</div>
          </div>

          <div className="filter-row">
            <div className="categories">
              {categories.map(item => (
                <button
                  key={item}
                  className={category === item ? 'category active' : 'category'}
                  onClick={() => setCategory(item)}
                >{item}</button>
              ))}
            </div>
            <span className="results-count">{filteredProducts.length} results</span>
          </div>

          {loading && <div className="message">Loading products from ShopSphere...</div>}
          {error && <div className="message error">{error}</div>}

          {!loading && !error && filteredProducts.length === 0 && (
            <div className="message">No products found. Try another search.</div>
          )}

          <div className="product-grid">
            {filteredProducts.map((product, index) => (
              <article className="product-card" key={product.id}>
                <div className="product-image">
                  <img
                    src={`https://images.unsplash.com/${images[index % images.length]}?w=650&q=80`}
                    alt={product.name}
                    loading="lazy"
                  />
                  <span className="product-tag">SHOPSPHERE PICK</span>
                  <button className="quick-add" onClick={() => addToCart(product)}>＋</button>
                </div>
                <div className="product-info">
                  <div className="product-category">EVERYDAY ESSENTIALS</div>
                  <h3>{product.name}</h3>
                  <div className="product-bottom">
                    <strong>{money(product.price)}</strong>
                    <button onClick={() => addToCart(product)}>Add to bag ↗</button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>
      </main>

      <footer className="footer">
        <a className="brand" href="#"><span className="brand-icon">S</span> ShopSphere<span className="brand-dot">.</span></a>
        <p>Discover more. Live better.</p>
        <span>© 2026 ShopSphere. Built with care.</span>
      </footer>

      {cartOpen && (
        <div className="overlay" onClick={() => setCartOpen(false)}>
          <aside className="cart-drawer" onClick={event => event.stopPropagation()}>
            <div className="cart-heading">
              <div><span className="eyebrow">YOUR SELECTION</span><h2>Your bag</h2></div>
              <button className="close-button" onClick={() => setCartOpen(false)}>×</button>
            </div>
            {orderResult ? (
              <div className="checkout-success">
                <span className="success-icon">✓</span>
                <h3>Order placed!</h3>
                <p>Your order has been created successfully.</p>
                {orderResult.map(result => (
                  <div className="order-result" key={result.order.id}>
                    <strong>{result.product}</strong>
                    <small>Order #{result.order.id}</small>
                    <small>Payment: {result.payment.status}</small>
                  </div>
                ))}
                <button className="primary-button drawer-button" onClick={() => {
                  setOrderResult(null)
                  setCartOpen(false)
                }}>
                  Continue shopping →
                </button>
              </div>
            ) : cart.length === 0 ? (
              <div className="empty-cart"><span>◇</span><h3>Your bag is empty</h3><p>Find something you love in our collection.</p></div>
            ) : (
              <>
                <div className="cart-items">
                  {cart.map(item => (
                    <div className="cart-item" key={item.id}>
                      <div><strong>{item.name}</strong><small>{money(item.price)}</small></div>
                      <div className="quantity">
                        <button onClick={() => changeQuantity(item.id, -1)}>−</button>
                        <span>{item.quantity}</span>
                        <button onClick={() => changeQuantity(item.id, 1)}>＋</button>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="cart-total"><span>Subtotal</span><strong>{money(cartTotal)}</strong></div>
                <p className="checkout-note">Enter your details to place your order. Payment is simulated for this project.</p>

                <form className="checkout-form" onSubmit={submitCheckout}>
                  <label>
                    Full name
                    <input
                      type="text"
                      value={customerName}
                      onChange={event => setCustomerName(event.target.value)}
                      placeholder="Enter your name"
                      required
                    />
                  </label>
                  <label>
                    Email address
                    <input
                      type="email"
                      value={customerEmail}
                      onChange={event => setCustomerEmail(event.target.value)}
                      placeholder="you@example.com"
                      required
                    />
                  </label>
                  {checkoutError && (
                    <p className="checkout-error">{checkoutError}</p>
                  )}
                  <button
                    className="primary-button drawer-button"
                    type="submit"
                    disabled={checkoutLoading}
                  >
                    {checkoutLoading ? 'Processing...' : 'Place order →'}
                  </button>
                </form>
              </>
            )}
            <button className="primary-button drawer-button" onClick={() => setCartOpen(false)}>
              Continue shopping <span>→</span>
            </button>
          </aside>
        </div>
      )}
    </div>
  )
}

export default App
