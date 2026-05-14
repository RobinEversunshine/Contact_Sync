from sync_contacts import main as push_to_gmails
from get_contact_info import main as get_contact


def main():
    payload = get_contact()
    push_to_gmails(payload)


if __name__ == "__main__":
    main()