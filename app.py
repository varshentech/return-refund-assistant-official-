
import os
import re
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import streamlit as st
from rag_engine import ask_policy


# ----------------------------- PROJECT PATHS -----------------------------

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "return_refund.db"
POLICY_PATH = APP_DIR / "policy.txt"


# ----------------------------- PAGE CONFIGURATION -----------------------------

st.set_page_config(
    page_title="Return & Refund Assistant",
    page_icon="📦",
    layout="wide"
)


# ----------------------------- DATABASE -----------------------------

def get_connection():
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                product TEXT NOT NULL,
                order_date TEXT NOT NULL,
                delivery_date TEXT,
                amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                status TEXT NOT NULL,
                sale_item INTEGER DEFAULT 0
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                reason TEXT NOT NULL,
                request_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                admin_note TEXT DEFAULT '',
                FOREIGN KEY(order_id) REFERENCES orders(order_id)
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM orders"
        ).fetchone()[0]

        if count == 0:
            today = date.today()

            samples = [
                (
                    "ORD1001", "Arun Kumar",
                    "Wireless Headphones",
                    (today - timedelta(days=12)).isoformat(),
                    (today - timedelta(days=3)).isoformat(),
                    2499.0, "UPI", "Delivered", 0
                ),
                (
                    "ORD1002", "Priya S",
                    "Running Shoes",
                    (today - timedelta(days=15)).isoformat(),
                    (today - timedelta(days=5)).isoformat(),
                    3199.0, "Card", "Delivered", 0
                ),
                (
                    "ORD1003", "Rahul M",
                    "Smart Watch",
                    (today - timedelta(days=20)).isoformat(),
                    (today - timedelta(days=10)).isoformat(),
                    4999.0, "UPI", "Delivered", 0
                ),
                (
                    "ORD1004", "Meena R",
                    "Bluetooth Speaker",
                    (today - timedelta(days=2)).isoformat(),
                    None,
                    1799.0, "Cash on Delivery", "Shipped", 0
                ),
                (
                    "ORD1005", "Karthik P",
                    "Sale T-shirt",
                    (today - timedelta(days=9)).isoformat(),
                    (today - timedelta(days=2)).isoformat(),
                    799.0, "UPI", "Delivered", 1
                )
            ]

            conn.executemany(
                "INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)",
                samples
            )


def get_order(order_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM orders WHERE order_id = ?",
            (order_id.strip().upper(),)
        ).fetchone()


def get_ticket(ticket_id):
    with get_connection() as conn:
        return conn.execute("""
            SELECT t.*, o.product, o.amount
            FROM tickets t
            JOIN orders o ON t.order_id = o.order_id
            WHERE t.ticket_id = ?
        """, (ticket_id,)).fetchone()


def create_ticket(order, reason, request_type):
    with get_connection() as conn:

        existing = conn.execute("""
            SELECT ticket_id
            FROM tickets
            WHERE order_id = ?
            AND status NOT IN ('Rejected', 'Completed')
        """, (order["order_id"],)).fetchone()

        if existing:
            return None, existing["ticket_id"]

        cur = conn.execute("""
            INSERT INTO tickets (
                order_id,
                customer_name,
                reason,
                request_type,
                created_at,
                status
            )
            VALUES (?, ?, ?, ?, ?, 'Pending')
        """, (
            order["order_id"],
            order["customer_name"],
            reason,
            request_type,
            date.today().isoformat()
        ))

        return cur.lastrowid, None


# ----------------------------- INITIALIZE DATABASE -----------------------------

init_db()


# ----------------------------- SIDEBAR -----------------------------

with st.sidebar:

    st.title("📦 ShopEasy Support")
    st.caption("Return & Refund Assistant")

    page = st.radio(
        "Navigate",
        [
            "AI Policy Assistant",
            "Order Lookup",
            "Create Return Request",
            "Track Ticket",
            "Admin Dashboard"
        ]
    )

    st.divider()
    st.caption("Demo application • Sample data only")


# ----------------------------- MAIN HEADER -----------------------------

st.title("📦 Return & Refund Assistant")
st.caption("E-commerce customer support portal | PRJ-121")


# ----------------------------- AI POLICY ASSISTANT -----------------------------

if page == "AI Policy Assistant":

    st.subheader(
        "Ask about returns, refunds and support policies"
    )

    st.info(
        "This AI assistant uses LangChain, ChromaDB and "
        "Gemini to understand customer questions, retrieve "
        "relevant policy information and generate "
        "customer-friendly answers."
    )

    q = st.text_input(
        "Your question",
        placeholder="Example: How many days do I have to return a product?"
    )

    if st.button("Ask AI Assistant", type="primary"):

        if q.strip():

            try:
                with st.spinner(
                    "AI assistant is analyzing your question..."
                ):

                    result = ask_policy(q)

                st.markdown(
                    "#### 🤖 AI Assistant Response"
                )

                st.write(result["answer"])

                if result["sources"]:
                    st.caption(
                        "Source: " + ", ".join(result["sources"])
                    )

            except Exception as e:

                st.error(
                    f"Unable to generate an AI response: {e}"
                )

        else:
            st.warning("Enter a question first.")

    with st.expander("Example questions"):

        st.write(
            "• How long do I have to return a product?\n"
            "• When will my refund be processed?\n"
            "• What if my product arrives damaged?\n"
            "• Can I cancel an order after shipping?"
        )


# ----------------------------- ORDER LOOKUP -----------------------------

elif page == "Order Lookup":

    st.subheader("Search your order")

    order_id = st.text_input(
        "Order ID",
        placeholder="ORD1001"
    ).strip().upper()

    if st.button("Search Order", type="primary"):

        if not order_id:
            st.warning("Enter an order ID.")

        else:
            order = get_order(order_id)

            if order:

                st.success("Order found")

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Order ID",
                    order["order_id"]
                )

                c2.metric(
                    "Amount",
                    f"₹{order['amount']:,.2f}"
                )

                c3.metric(
                    "Status",
                    order["status"]
                )

                st.write(
                    f"**Customer:** {order['customer_name']}  \n"
                    f"**Product:** {order['product']}  \n"
                    f"**Order date:** {order['order_date']}  \n"
                    f"**Delivery date:** {order['delivery_date'] or 'Not delivered'}  \n"
                    f"**Payment:** {order['payment_method']}"
                )

            else:
                st.error(
                    "No order found. Check the ID and try again."
                )

    with st.expander("Demo order IDs"):

        st.code(
            "ORD1001  ORD1002  ORD1003  ORD1004  ORD1005"
        )


# ----------------------------- RETURN REQUEST -----------------------------

elif page == "Create Return Request":

    st.subheader(
        "Create a return / replacement request"
    )

    st.write(
        "Enter a delivered order ID. Eligibility is checked "
        "against the sample return policy."
    )

    order_id = st.text_input(
        "Order ID",
        key="return_order",
        placeholder="ORD1001"
    ).strip().upper()

    reason = st.selectbox(
        "Reason",
        [
            "Damaged or defective product",
            "Wrong product received",
            "Product not as expected",
            "Other"
        ]
    )

    details = st.text_area(
        "Additional details",
        placeholder="Describe the issue briefly"
    )

    request_type = st.radio(
        "Requested resolution",
        ["Return and refund", "Replacement"],
        horizontal=True
    )

    if st.button(
        "Check Eligibility & Submit",
        type="primary"
    ):

        order = get_order(order_id) if order_id else None

        if not order:

            st.error(
                "Order not found. Use a valid order ID."
            )

        elif order["status"] != "Delivered" or not order["delivery_date"]:

            st.error(
                "This order has not been delivered. "
                "A return request cannot be created yet."
            )

        else:

            delivered = date.fromisoformat(
                order["delivery_date"]
            )

            days = (date.today() - delivered).days

            is_damaged = (
                reason == "Damaged or defective product"
            )

            if days < 0:

                st.error(
                    "Invalid delivery date. Contact support."
                )

            elif days > 7:

                st.error(
                    f"Not eligible: the order was delivered "
                    f"{days} days ago. The standard return "
                    f"window is 7 days."
                )

            elif (
                is_damaged
                and request_type == "Replacement"
                and days > 2
            ):

                st.error(
                    "The supplied policy requires "
                    "damaged-product replacement requests "
                    "within 48 hours of delivery. You may "
                    "select return and refund if still within "
                    "the 7-day return window."
                )

            elif (
                order["sale_item"]
                and request_type == "Return and refund"
            ):

                st.error(
                    "Sale items are eligible for replacement "
                    "only, not refund, under the supplied policy."
                )

            elif not details.strip():

                st.warning(
                    "Please provide a short description "
                    "before submitting."
                )

            else:

                ticket_id, existing_id = create_ticket(
                    order,
                    f"{reason}: {details.strip()}",
                    request_type
                )

                if existing_id:

                    st.warning(
                        "An active request already exists "
                        f"for this order. Ticket ID: {existing_id}"
                    )

                else:

                    st.success(
                        "Request submitted successfully. "
                        f"Your ticket ID is **TKT-{ticket_id:04d}**."
                    )

                    st.info(
                        "Current status: Pending. "
                        "Keep your ticket ID to track the request."
                    )


# ----------------------------- TRACK TICKET -----------------------------

elif page == "Track Ticket":

    st.subheader(
        "Track your return / refund request"
    )

    ticket_input = st.text_input(
        "Ticket ID",
        placeholder="TKT-0001"
    )

    if st.button("Track Request", type="primary"):

        match = re.search(
            r"(\d+)",
            ticket_input
        )

        ticket = (
            get_ticket(int(match.group(1)))
            if match else None
        )

        if ticket:

            st.success("Ticket found")

            st.metric(
                "Current status",
                ticket["status"]
            )

            st.write(
                f"**Ticket:** TKT-{ticket['ticket_id']:04d}  \n"
                f"**Order:** {ticket['order_id']}  \n"
                f"**Product:** {ticket['product']}  \n"
                f"**Request:** {ticket['request_type']}  \n"
                f"**Reason:** {ticket['reason']}  \n"
                f"**Created:** {ticket['created_at']}  \n"
                f"**Admin note:** {ticket['admin_note'] or 'No update yet'}"
            )

        else:

            st.error(
                "Ticket not found. Check the ticket ID."
            )


# ----------------------------- ADMIN DASHBOARD -----------------------------

elif page == "Admin Dashboard":

    st.subheader("Admin Dashboard")

    st.warning(
        "Demo admin access. For an academic prototype only; "
        "configure ADMIN_PASSWORD as an environment variable "
        "before any real deployment."
    )

    expected = os.getenv(
        "ADMIN_PASSWORD",
        "admin123"
    )

    password = st.text_input(
        "Admin password",
        type="password"
    )

    if password == expected:

        with get_connection() as conn:

            total_orders = conn.execute(
                "SELECT COUNT(*) FROM orders"
            ).fetchone()[0]

            total_tickets = conn.execute(
                "SELECT COUNT(*) FROM tickets"
            ).fetchone()[0]

            pending = conn.execute(
                "SELECT COUNT(*) FROM tickets WHERE status='Pending'"
            ).fetchone()[0]

            completed = conn.execute(
                "SELECT COUNT(*) FROM tickets WHERE status='Completed'"
            ).fetchone()[0]

            rows = conn.execute("""
                SELECT
                    t.ticket_id,
                    t.order_id,
                    t.customer_name,
                    t.request_type,
                    t.reason,
                    t.created_at,
                    t.status,
                    t.admin_note
                FROM tickets t
                ORDER BY t.ticket_id DESC
            """).fetchall()

        a, b, c, d = st.columns(4)

        a.metric("Total orders", total_orders)
        b.metric("Total tickets", total_tickets)
        c.metric("Pending", pending)
        d.metric("Completed", completed)

        st.markdown(
            "#### Return request management"
        )

        if rows:

            for row in rows:

                with st.expander(
                    f"TKT-{row['ticket_id']:04d} | "
                    f"{row['order_id']} | {row['status']}"
                ):

                    st.write(
                        f"**Customer:** {row['customer_name']}  \n"
                        f"**Type:** {row['request_type']}  \n"
                        f"**Reason:** {row['reason']}  \n"
                        f"**Created:** {row['created_at']}"
                    )

                    statuses = [
                        "Pending",
                        "Approved",
                        "Rejected",
                        "Processing",
                        "Completed"
                    ]

                    current_status = row["status"]

                    new_status = st.selectbox(
                        "Update status",
                        statuses,
                        index=(
                            statuses.index(current_status)
                            if current_status in statuses
                            else 0
                        ),
                        key=f"status_{row['ticket_id']}"
                    )

                    note = st.text_input(
                        "Admin note",
                        value=row["admin_note"],
                        key=f"note_{row['ticket_id']}"
                    )

                    if st.button(
                        "Save Update",
                        key=f"save_{row['ticket_id']}"
                    ):

                        with get_connection() as conn:

                            conn.execute("""
                                UPDATE tickets
                                SET status = ?, admin_note = ?
                                WHERE ticket_id = ?
                            """, (
                                new_status,
                                note,
                                row["ticket_id"]
                            ))

                        st.success(
                            "Ticket updated. Refresh the page "
                            "to see the latest dashboard totals."
                        )

        else:

            st.info(
                "No return requests have been submitted yet."
            )

        st.markdown(
            "#### Sample order records"
        )

        with get_connection() as conn:

            order_rows = conn.execute("""
                SELECT
                    order_id,
                    customer_name,
                    product,
                    amount,
                    status
                FROM orders
                ORDER BY order_id
            """).fetchall()

        st.dataframe(
            [dict(r) for r in order_rows],
            use_container_width=True,
            hide_index=True
        )

    elif password:

        st.error(
            "Incorrect admin password."
        )


# ----------------------------- FOOTER -----------------------------

st.divider()

st.caption(
    "Academic prototype for PRJ-121 | Uses local sample data; "
    "no real payments or refunds are processed."
)
