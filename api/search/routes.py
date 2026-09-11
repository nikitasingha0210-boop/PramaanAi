from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.deps import get_current_user
from api.auth.models import User
from api.tenders.models import Tender, Bidder, BidderSubmission

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def universal_search(q: str = Query(min_length=1), db: Session = Depends(get_db),
                      user: User = Depends(get_current_user)):
    like = f"%{q}%"
    tenders = db.query(Tender).filter((Tender.code.ilike(like)) | (Tender.title.ilike(like))).limit(8).all()
    bidders = db.query(Bidder).filter(
        (Bidder.name.ilike(like)) | (Bidder.pan.ilike(like)) | (Bidder.gstin.ilike(like)) |
        (Bidder.cin.ilike(like)) | (Bidder.udyam.ilike(like))
    ).limit(8).all()

    results = []
    for t in tenders:
        results.append({"type": "tender", "id": t.id, "title": t.title, "subtitle": t.code})
    for b in bidders:
        results.append({"type": "bidder", "id": b.id, "title": b.name, "subtitle": b.gstin or b.pan or b.cin or ""})
        submissions = db.query(BidderSubmission).filter(BidderSubmission.bidder_id == b.id).all()
        for s in submissions:
            results.append({
                "type": "submission", "id": s.id, "title": f"{b.name} · {s.tender.code}",
                "subtitle": f"Status: {s.status.value}",
            })
    return results
